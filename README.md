About
=====

This module provides the **mysqltotsv.Splitter** class and a CLI tool to allow conversion
of large MySQL dumps to the [TSV format](https://en.wikipedia.org/wiki/Tab-separated_values). 

The module assumes the MySQL dump to be encoded in [UTF-8 format](https://en.wikipedia.org/wiki/UTF-8).

This is primarily intended for large MySQL dumps where opening them with a text editor is impractical
and handling them is easier through a tool.

Install
=======

To install from pypi:

    pip3 install --user mysqltotsv

Usage
=====

The following command takes a MySQL dump and creates a separate TSV file for each
table found inside (the output directory needs to be present):

    python3.7 mysql-to-tsv.py --file dump.sql --outdir out1

There is also a switch to only process certain tables and skip the rest. Example:

    python3.7 mysql-to-tsv.py --file dump.sql --outdir out1 --table-filter=updates,updates_edited

More details about the CLI switches:

```
usage: mysql-to-tsv.py [-h] --file FILE --outdir OUTDIR
                       [--table-filter TABLE_FILTER] [--only-schema]
                       [--strip-quotes] [--debug] [--ignore-errors]
                       [--estimate1] [--estimate2]

Tool for conversion of large MySQL dumps to TSV format

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           mysql dump file
  --outdir OUTDIR       output directory
  --table-filter TABLE_FILTER
                        filtered tables
  --only-schema         write the schema to the output directory
  --strip-quotes        strip quotes from values
  --debug               print debug information
  --ignore-errors       ignore processing errors
  --estimate1           estimate row counts for each table inside the sql file
  --estimate2           estimate row counts for each table inside the sql file
```

Support
==================

For questions or requests for paid support, please send an e-mail to stefan.petrea@gmail.com

