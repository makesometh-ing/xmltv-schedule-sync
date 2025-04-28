# XMLTV Schedule Sync

This script does one thing only and it does it very well.

It will take an existing XMLTV file and given schedule sources, pull and merge them into the XMLTV compatible XML file and output an updated file.

- an XMLTV compatible input XML file of channel listings
- a CSV containing mappings between your target channel ID in the XMLTV file and an URL from which to fetch schedules for that specific channel

## Usage

Example xmltv.xml and CSVs are in the `samples` file

```python
python run.py --xmltv-file=./path/to/xmltv.xml --schedule-sources= ./path/to/schedule_soruces.csv
```

## Possible improvements

- allow multiple sources in schedule source XML files


## EPG sources:

- I use this one: https://epg.pw/index.html?lang=en
