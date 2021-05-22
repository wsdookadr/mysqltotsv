#!/usr/bin/python3
import argparse
import os.path
import re
from mysqltotsv import Splitter, ExtractSchema, Estimate1, Estimate2, row_strip_quotes

def valid_file(inputfile):
    if not os.path.isfile(inputfile):
        raise argparse.ArgumentTypeError('mysql dump file does not exist')
    return inputfile

def valid_dir(outputdir):
    if not os.path.isdir(outputdir):
        raise argparse.ArgumentTypeError('output directory does not exist')
    return outputdir

arg_parser = argparse.ArgumentParser(description='Tool for conversion of large MySQL dumps to TSV format')
arg_parser.add_argument('--file', dest='file', action='store', required=True, type=valid_file, help='mysql dump file')
arg_parser.add_argument('--outdir', dest='outdir', action='store', required=True, type=valid_dir, help='output directory')
arg_parser.add_argument('--table-filter', dest='table_filter', action='store', required=False, type=str, help='filtered tables')
arg_parser.add_argument('--only-schema', dest='only_schema', action='store_true', help='write the schema to the output directory')
arg_parser.add_argument('--strip-quotes', dest='strip_quotes', action='store_true', help='strip quotes from values')
arg_parser.add_argument('--debug', dest='debug', action='store_true', help='print debug information')
arg_parser.add_argument('--ignore-errors', dest='ignore_errors', action='store_true', help='ignore processing errors')
arg_parser.add_argument('--estimate1', dest='estimate1', action='store_true', help='estimate row counts for each table inside the sql file')
arg_parser.add_argument('--estimate2', dest='estimate2', action='store_true', help='estimate row counts for each table inside the sql file')

args   = arg_parser.parse_args()

if  args.estimate1:
    estimate = Estimate1(args)
    estimate.doit()
    estimate.print()
elif args.estimate2:
    estimate = Estimate2(args)
    estimate.doit()
    estimate.print()
elif args.only_schema:
    extract = ExtractSchema(args)
    extract.doit()
else:
    splitter = Splitter(args)
    rows_written = 0
    seen_outfile = set()

    batch_gen = splitter.next_batch()
    while True:
        batch = None
        try:
            batch = next(batch_gen)
        except StopIteration as e:
            break
        except Exception as e:
            if args.ignore_errors:
                print(e)
            else:
                raise e

        if args.ignore_errors and batch["parse_exc"]:
            continue

        outfile = os.path.join(args.outdir,batch["table_name"] + ".tsv")
        if os.path.exists(outfile) and outfile not in seen_outfile:
            os.remove(outfile)

        seen_outfile |= set([outfile])

        with open(outfile,"a") as fh_out:
            rows_written += len(batch["rows"])
            for r in batch["rows"]:
                if args.strip_quotes:
                    row_strip_quotes(r)
                fh_out.write("\t".join(map(str, r)) + "\n")
            print("rows written: ",rows_written)

