import argparse
import xml.etree.ElementTree as ET
import csv
from typing import Dict, List
import requests

#####
# cli args
#####
parser = argparse.ArgumentParser(
                    prog='XMLTV Schedule Sync',
                    description='Syncs and merges remote EPG schedules into an XMLTV compatible file',
                  )

parser.add_argument('-x', '--xmltv-file', type=str, help='Path to the XMLTV file to update', required=True)
parser.add_argument('-s', '--schedule-sources', type=str, help='Path to the CSV file containing schedule sources', required=True)
#####
# cli args end
#####



def __main__(xmltv_file: str, schedule_sources: str) -> None:
  print(f"Updating {xmltv_file} with schedules from {schedule_sources}")

  # 1. Parse XMLTV file
  try:
    tree = ET.parse(xmltv_file)
    root = tree.getroot()
  except FileNotFoundError:
    print(f"Oops, can't find your file: {xmltv_file}")
    return

  # 2. Parse CSV file
  try:
    with open(schedule_sources, newline='', encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile)
      sources: List[Dict[str, str]] = [row for row in reader]
  except FileNotFoundError:
    print(f"Oops, can't find your file: {schedule_sources}")
    return

  # 3. Build a lookup for sources by epg_channel_id
  sources_by_id: Dict[str, Dict[str, str]] = {
    row['epg_channel_id']: row for row in sources if 'epg_channel_id' in row
  }

  # 4. For each channel in the XMLTV file
  for channel in root.findall('channel'):
    channel_id = channel.get('id')
    if not channel_id:
      continue

    source_row = sources_by_id.get(channel_id)
    if not source_row:
      continue

    schedule_url = source_row.get('schedule_source')
    if not schedule_url:
      continue

    print(f"Fetching schedule for channel {channel_id} from {schedule_url}...")

    try:
      response = requests.get(schedule_url, timeout=10)
      response.raise_for_status()
      remote_tree = ET.ElementTree(ET.fromstring(response.content))
      remote_root = remote_tree.getroot()
    except Exception as e:
      print(f"  Failed to fetch or parse remote XML for channel {channel_id}: {e}")
      continue

    # REMOVE all existing <programme> elements for this channel
    programmes_to_remove = [
      prog for prog in root.findall('programme')
      if prog.get('channel') == channel_id
    ]
    for prog in programmes_to_remove:
      root.remove(prog)

    # INSERT new <programme> elements for this channel
    for programme in remote_root.findall('programme'):
      # Set the channel attribute to the local channel_id
      programme.set('channel', channel_id)
      root.append(programme)

  # 6. Save the updated XMLTV file
  tree.write(xmltv_file, encoding='utf-8', xml_declaration=True)
  print(f"Updated XMLTV file saved to {xmltv_file}")


if __name__ == "__main__":
  args = parser.parse_args()

  __main__(xmltv_file=args.xmltv_file, schedule_sources=args.schedule_sources)


