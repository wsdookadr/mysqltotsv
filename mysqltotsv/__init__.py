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

cell: NUMBER | ESCAPED_STRING1 | ESCAPED_STRING2 | "NULL"

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
        return cells[0]

    def start(self, items):
        return items[0]

    def cells(self, cells):
        if len(cells) == 1:
            rv = cells[0]
        else:
            if isinstance(cells[1],str):
                rv = cells[0],cells[1]
            elif isinstance(cells[1],tuple):
                rv = cells[0],*cells[1]
        return rv

    def cell(self, cell):
        return re.sub(r"\t","",cell[0].value)

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
                num+=1
                tbl_name = g.groups()[0]

                if len(self.table_filter) > 0 and tbl_name not in self.table_filter:
                    continue

                line = re.sub(r"INSERT INTO `([^\`]+)` ","",line)
                line = re.sub(r" VALUES ",", ",line)
                line = re.sub(r";\s*$","", line)
                tree = parser.parse(line)

                rows = list(ProcessAST().transform(tree))
                if tbl_name in self.seen_table:
                    rows.pop(0)
                self.seen_table |= set([tbl_name])

                yield { "table_name": tbl_name, "rows": rows }

        self.fh.close()
        yield None


