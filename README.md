# energieag-verbrauch
Outputs the total power consumption for an EnergieAG energy contract.

## How to use
```
eag.py -h
usage: eag.py [-h] --user USER --password PASSWORD

Stromverbrauch auslesen.

optional arguments:
  -h, --help           show this help message and exit
  --user USER          the user to login to the webinterface
  --password PASSWORD  the password
```

## Example
```
eag.py --user vip_customer --password verysecret
1921.63
```

The result is in kWh!