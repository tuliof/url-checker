# URL Checker

## Usage

```
checkUrl.py [options] urlsFile machineSerialNumber

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d, --debug           print the url and the request result[default: False]
  -o FILE, --output=FILE
                        write output to FILE, will write result.csv
                        to same path as the program if none is provided.
  -t, --threaded        if set to true will run concurrent requests, it will
                        speed up the test.
```

## Generate a executable:
You will need to have py2exe installed - www.py2exe.org.

Run on the shell ``python setup.py py2exe``

## To do
- Change option -d (debug) to -v (verbose)
