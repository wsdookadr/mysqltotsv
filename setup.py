import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mysqltotsv",
    version="0.1.2",
    author="Stefan Corneliu Petrea",
    author_email="stefan@garage-coding.com",
    description="Tool for conversion of MySQL dumps to TSV format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://blog.garage-coding.com/",
    packages=setuptools.find_packages(),
    scripts=["mysql-to-tsv.py"],
    install_requires=[
          'lark-parser>=0.11.1',
    ],
    extras_require={
        'lark-parser': ["regex"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
