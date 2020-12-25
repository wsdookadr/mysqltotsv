About
=====

This module provides the **mysqltotsv.Splitter** class and a CLI tool to allow conversion
of large MySQL dumps to the TSV format. 

The module assumes the MySQL dump to be encoded in UTF-8 format.

Install
=======

To install from pypi:

    pip3 install --user mysql-to-tsv

Usage
=====

The following command takes a MySQL dump and creates a separate TSV file for each
table found inside:

    python3.7 mysql-to-tsv.py --file dump.sql --outdir out1

There is also a switch to only process certain tables and skip the rest. Example:

    python3.7 mysql-to-tsv.py --file dump.sql --outdir out1 --table-filter=updates,updates_edited

More details about the CLI switches:

```
usage: mysql-to-tsv.py [-h] --file FILE --outdir OUTDIR
                       [--table-filter TABLE_FILTER]

Tool for conversion of large MySQL dumps to TSV format

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           mysql dump file
  --outdir OUTDIR       output directory
  --table-filter TABLE_FILTER
                        filtered tables
```

Support
==================

For questions or requests for paid support, please send an e-mail to business@garage-coding.com

