letrac
======

The program to do logic extraction. Written in python and simply running it with one perl script. 
This program is the implementation of the following paper:

http://www.cs.utexas.edu/~ml/papers/wasp-logic-acl-07.pdf

Installation
=====
This software uses additional alignment software https://github.com/neubig/pialign to do word alignment. 
You need to install it first so it can be referenced from letrac.

Data
=====
You can download the data that is used for this software by clicking this link: 

ftp://ftp.cs.utexas.edu/pub/mooney/nl-ilp-data/geosystem/geoqueries880

There is also smaller version of the data (only 250 lines):

ftp://ftp.cs.utexas.edu/pub/mooney/nl-ilp-data/geosystem/geoqueries250

Running
=====
To run the program, simply run the **run-extraction.pl** with some necessary options. 
Given now you are in your working directory, the sample of running the extraction is:

```bash
[LETRAC_DIR]/run-extraction.pl -pialign-dir [PIALIGN_DIR] -working-dir [OUTPUT_FOLDER] -input [GEOQUERY_INPUT] -letrac-dir [LETRAC_DIR]
```
