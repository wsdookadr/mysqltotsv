import argparse
from mysqltotsv import Splitter

class MockArgs:
    def __init__(self): pass

def test_next_batch():
    import logging
    args = MockArgs()
    args.table_filter = ""
    args.file = "tests/t1.sql"
    args.outdir = "tests/"
    splitter = Splitter(args)

    expected = {'table_name': 't1_tmp', 'rows': [('`col1`', '`col2`', '`col3`', '`col4`'), ('1', "'abc'", "'def'", '4'), ('2', "'ghi'", "'jkl'", '5'), ('3', "'zke'", "'maa'", '7')]}
    got = next(splitter.next_batch())
    assert got == expected

