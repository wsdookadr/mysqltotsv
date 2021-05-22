import re
import os.path
import logging
import sys
from lark import Lark, logger as lark_logger
from lark import Transformer
sys.setrecursionlimit(50000)

parser = Lark(r"""
_STRING_INNER: /(.*?)/
_STRING_ESC_INNER: _STRING_INNER /(?<!\\)(\\\\)*?/
ESCAPED_STRING1: "'" _STRING_ESC_INNER "'"
ESCAPED_STRING2: "`" _STRING_ESC_INNER "`"

start: records+ ";" ?

records: record | record "," records

record: "(" cells ")"

cells: cell | cell "," cells

NULL: "NULL"

cell: NUMBER | ESCAPED_STRING1 | ESCAPED_STRING2 | NULL

%import common (WS_INLINE, NUMBER)
%ignore WS_INLINE
""", parser='lalr', start='start', regex=True)


class ProcessAST(Transformer):
    def records(self, records):
        if len(records) == 1:
            rv = tuple([records[0]])
        else:
            rv = records[0], *records[1]
        return rv

    def record(self, cells):
        return list(cells[0])

    def start(self, items):
        return items[0]

    def cells(self, cells):
        if len(cells) == 1:
            rv = cells[0]
        else:
            if isinstance(cells[1],(str,int,float,)):
                rv = cells[0],cells[1]
            elif isinstance(cells[1],tuple):
                rv = cells[0],*cells[1]
        return rv

    def cell(self, cell):
        if   re.match(r'^\d+(?:\.\d+)$', cell[0].value):
            return float(cell[0].value)
        elif re.match(r'^\d+$', cell[0].value):
            return int(cell[0].value)
        else:
            return re.sub(r"\t","",cell[0].value)

class Estimate1:

    def __init__(self, args):
        self.args = args

    def doit(self):
        fh = open(self.args.file,"rb")
        counts = {}
        for line in fh:
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError as e:
                decoded_unicode = line.decode('utf-8', 'replace')
                line = decoded_unicode

            m_insert = re.match(r"^INSERT INTO `([^\`]+)`", line)
            if m_insert:
                tbl_name = m_insert.groups()[0]
                cnt_rows = line.count("),(") + 1
                if tbl_name not in counts:
                    counts[tbl_name] = cnt_rows
                else:
                    counts[tbl_name] += cnt_rows
        self.counts = counts
        return counts

    def print(self):
        for k in sorted(self.counts.keys()):
            print(k,self.counts[k])

class Estimate2:

    def __init__(self, args):
        self.args = args

    def doit(self):
        fh = open(self.args.file,"rb")
        counts = {}
        for line in fh:
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError as e:
                decoded_unicode = line.decode('utf-8', 'replace')
                line = decoded_unicode

            m_insert = re.match(r"^INSERT INTO `([^\`]+)`", line)
            if m_insert:
                tbl_name = m_insert.groups()[0]
                line = re.sub(r"INSERT INTO `([^\`]+)` ","",line)
                line = re.sub(r" VALUES ",", ",line)
                line = re.sub(r";\s*$","", line)
                try:
                    tree = parser.parse(line)
                    cnt_rows = len(list(ProcessAST().transform(tree)))
                    if tbl_name not in counts:
                        counts["tbl_name"] = cnt_rows
                    else:
                        counts["tbl_name"] += cnt_rows
                except Exception as e:
                    pass
        self.counts = counts
        return counts

    def print(self):
        for k in sorted(self.counts.keys()):
            print(k,self.counts[k])

class ExtractSchema:
    def __init__(self, args):
        self.args = args

    def doit(self):
        self.in_fh = open(self.args.file,"rb")
        self.out_fh = open(os.path.join(self.args.outdir,"schema.sql"),"w")

        STATE1,STATE2=1,2
        state = 1

        buf = ""

        for line in self.in_fh:
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError as e:
                decoded_unicode = line.decode('utf-8', 'replace')
                line = decoded_unicode

            tbl_name = None
            g1 = re.match(r"^CREATE TABLE ", line)
            g2 = re.match(r"^\).*;", line)

            if state == STATE1 and g1:
                buf += line
                state = STATE2
            elif state == STATE2 and g2:
                buf += line
                state = STATE1
            elif state == STATE2:
                buf += line

        self.out_fh.write(buf)
        self.out_fh.close()
        self.in_fh.close()

class Splitter:
    def __init__(self, args):
        lark_logger.setLevel(logging.DEBUG)
        self.args = args
        if self.args.table_filter:
            self.table_filter = self.args.table_filter.split(",")
        else:
            self.table_filter = []

        self.fh = open(self.args.file,"rb")
        self.seen_table = set()

    def next_batch(self):
        num = 0
        for line in self.fh:
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError as e:
                decoded_unicode = line.decode('utf-8', 'replace')
                line = decoded_unicode

            tbl_name = None
            g = re.match(r"^INSERT INTO `([^\`]+)`", line)

            if g:
                tbl_name = g.groups()[0]

                if len(self.table_filter) > 0 and tbl_name not in self.table_filter:
                    continue
                num+=1
                if self.args.debug:
                    print("line num: ",num)

                line = re.sub(r"INSERT INTO `([^\`]+)` ","",line)
                line = re.sub(r" VALUES ",", ",line)
                line = re.sub(r";\s*$","", line)

                parse_exc = None
                rows = []
                try:
                    tree = parser.parse(line)
                    rows = list(ProcessAST().transform(tree))
                    if tbl_name in self.seen_table:
                        rows.pop(0)
                    self.seen_table |= set([tbl_name])
                except Exception as e:
                    parse_exc = e

                yield { "table_name": tbl_name, "rows": rows, "parse_exc": parse_exc }

        self.fh.close()



def row_strip_quotes(r):
    for i in range(len(r)):
        if isinstance(r[i], str):
            if (r[i].startswith("'")  and r[i].endswith("'")):
                r[i] = re.sub(r"^'","",re.sub(r"'$","",r[i]))
                continue
            if (r[i].startswith("\"") and r[i].endswith("\"")):
                r[i] = re.sub(r'^"',"",re.sub(r'"$',"",r[i]))
                continue
            if (r[i].startswith("`")  and r[i].endswith("`")):
                r[i] = re.sub(r'^`',"",re.sub(r'`$',"",r[i]))
                continue

