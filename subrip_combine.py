# -*- coding: utf-8 -*-

"""
joins two subrip formatted files together and allows adjustment of timestamp offsets
does no special error checking, but should work with the vast majority of english subs
"""

import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--one", dest="one", metavar="FILE", help="first input file", required=True)
parser.add_argument("--two", dest="two", metavar="FILE", help="second input file", required=True)
parser.add_argument("--outfile", dest="outfile", metavar="FILE", help="output file", required=True)
parser.add_argument("--hours", dest="hours", type=int, metavar="N", help="offset second file by N hours", default=0)
parser.add_argument("--minutes", dest="minutes", type=int, metavar="N", help="offset second file by N minutes", default=0)
parser.add_argument("--seconds", dest="seconds", type=int, metavar="N", help="offset second file by N seconds", default=0)
args = parser.parse_args()

offset = datetime.timedelta(hours=args.hours, minutes=args.minutes, seconds=args.seconds)

line_no = 0
keep_lines = []

with open(args.one, "r") as infile_a:
  data = infile_a.read()
  keep_lines = data.split("\n")
  for line in keep_lines:
    if line.strip().isdigit():
      line_no = int(line)
    elif " --> " in line:
      last_timecodes = line

first_h, first_m, first_s, first_ms = last_timecodes.split(" --> ")[1].replace(",", ":").split(":") 
firstfile_offset = datetime.timedelta(hours=int(first_h), minutes=int(first_m), seconds=int(first_s), milliseconds=int(first_ms))
print "first file ended on line {}".format(line_no)

def twiddle_time(time_string):
  old_h, old_m, old_s, old_ms = time_string.replace(",", ":").split(":")
  old_time = datetime.timedelta(hours=int(old_h), minutes=int(old_m), seconds=int(old_s), milliseconds=int(old_ms))
  total_secs = (old_time + firstfile_offset + offset).total_seconds()
  hours, remainder = divmod(int(total_secs), 60*60)
  minutes, seconds = divmod(remainder, 60) 
  _, millisecs = divmod(total_secs, 1)
  millisecs = int(millisecs * 1000)
  new_time = "{:02}:{:02}:{:02},{:03}".format(hours, minutes, seconds, millisecs)
  return new_time

with open(args.two, "r") as infile_b:
  data = infile_b.read()
  mod_lines = data.split("\n")
  for line in mod_lines:
    # no idea what the goofy string is that appears in front of the first line.
    # maybe some kind of magic number for file identification?  anyway, count it as a line
    if line.strip().isdigit() or line.startswith("﻿1"):
      line_no += 1
      keep_lines.append(str(line_no))
    elif " --> " in line:
      start_time, stop_time = line.split(" --> ")
      new_start = twiddle_time(start_time)
      new_stop = twiddle_time(stop_time)
      keep_lines.append("{} --> {}".format(new_start, new_stop))
    else:
      keep_lines.append(line)
      
with open(args.outfile, "w") as outfile:
  outfile.write("\n".join(keep_lines))
  outfile.flush()
  outfile.close()
