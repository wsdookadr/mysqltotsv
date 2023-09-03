import argparse
from mysqltotsv import Splitter, ProcessAST, row_strip_quotes

class MockArgs:
    def __init__(self): pass

def test_ProcessAST_type_conversion():
    p = ProcessAST()
    class o:
        def __init__(self): pass
    o1 = o()
    o1.value = '123'
    assert type(p.cell([o1])) == int
    o1.value = '12.34'
    assert type(p.cell([o1])) == float
    o1.value = "'str'"
    assert type(p.cell([o1])) == str

def test_next_batch_single():
    args = MockArgs()
    args.table_filter = ""
    args.file = "tests/t0.sql"
    args.outdir = "tests/"
    args.debug = False
    splitter = Splitter(args)

    expected = {'table_name': 't1_tmp', 'rows': [['`col1`', '`col2`', '`col3`', '`col4`'], [1, "'abc'", "'def'", 4]], 'parse_exc': None}
    got = next(splitter.next_batch())
    assert got == expected

def test_next_batch_multiple():
    args = MockArgs()
    args.table_filter = ""
    args.file = "tests/t1.sql"
    args.outdir = "tests/"
    args.debug = False
    splitter = Splitter(args)

    expected = {'table_name': 't1_tmp', 'rows': [['`col1`', '`col2`', '`col3`', '`col4`'], [1, "'abc'", "'def'", 4], [2, "'ghi'", "'jkl'", 5], [3, "'zke'", "'maa'", 7]],'parse_exc': None}
    got = next(splitter.next_batch())
    assert got == expected

def test_next_batch_withnull():
    args = MockArgs()
    args.table_filter = ""
    args.file = "tests/t2.sql"
    args.outdir = "tests/"
    args.debug = False
    splitter = Splitter(args)
    got = next(splitter.next_batch())

    expected = {'table_name': 't1_tmp', 'rows': [['`col1`', '`col2`', '`col3`', '`col4`'], ['NULL', "'abc'", "'def'", 'NULL']],'parse_exc': None}
    assert got == expected

def test_invalid_insert():
    args = MockArgs()
    args.table_filter = ""
    args.file = "tests/t3.sql"
    args.outdir = "tests/"
    args.debug = False
    splitter = Splitter(args)

    got = next(splitter.next_batch())
    assert got['parse_exc'] is not None

def test_insert_into_without_column_names():
    args = MockArgs()
    args.table_filter = ""
    args.file = "tests/t4.sql"
    args.outdir = "tests/"
    args.debug = False
    splitter = Splitter(args)

    got = next(splitter.next_batch())

    assert len(got['rows']) == 1

def test_row_strip_quotes():
    r = ['NULL', "'abc'", "`def`", 'NULL']
    expected = ['NULL', "abc", "def", 'NULL']
    row_strip_quotes(r)
    assert r == expected

