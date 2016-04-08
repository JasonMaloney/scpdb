#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import csv
import sqlite3

gci_map = {
        'B17 PCI': ['0F', '10', '11', '12'],
        'B4 PCI 1': ['16', '17', '18', '19'],
        'B2 PCI': ['08', '09', '0A', '0B'],
        'B4 PCI 2': ['32', '33', '34', '35'],
        'B5 PCI': ['01', '02', '03', '04'],
        }

# CREATE TABLE sites_lte (_id INTEGER PRIMARY KEY, first_time NUMERIC, first_time_offset NUMERIC, last_time NUMERIC, last_time_offset NUMERIC, last_device_latitude NUMERIC, last_device_longitude NUMERIC, last_device_loc_accuracy NUMERIC, user_note TEXT, provider TEXT, plmn NUMERIC, gci TEXT, pci NUMERIC, tac NUMERIC, dl_chan NUMERIC, strongest_rsrp NUMERIC, strongest_latitude NUMERIC, strongest_longitude NUMERIC)

if len(sys.argv) < 3:
    print('Usage: ' + sys.argv[0] + ' csvfile dbfile')
    sys.exit(1)

conn = sqlite3.connect(sys.argv[2])
c = conn.cursor()

def insert(tac, gci, pci, lat, lon, name, conf):
    global c
    record = (
            name,
            'AT&T',
            '310410',
            gci,
            pci,
            tac,
            '-60' if conf else '-140',
            lat,
            lon,
            )
    c.execute("""INSERT INTO sites_lte
            (user_note,
            provider,
            plmn,
            gci,
            pci,
            tac,
            strongest_rsrp,
            strongest_latitude,
            strongest_longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", record)

with open(sys.argv[1], 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    cols = {x:ind for ind, x in enumerate(next(csvreader))}
    for row in csvreader:
        name = row[cols['Name']]
        if name.endswith('*'):
            name = name[:-1]
        confirmed = True
        if 'CONFIRM' in row[cols['Notes']]:
            confirmed = False
            name = name + ' NEW'
        for gci_col in ['LTE GCI 1', 'LTE GCI 2', 'LTE GCI 3']:
            gci = row[cols[gci_col]]
            if gci:
                for pci_col in gci_map:
                    pcis = row[cols[pci_col]]
                    if pcis:
                        for idx, pci in enumerate(pcis.split(',')):
                            pci = pci.strip()
                            if pci != '?' and pci.isdigit():
                                insert(row[cols['TAC']],
                                        gci[:6] + gci_map[pci_col][idx],
                                        pci,
                                        row[cols['LAT']],
                                        row[cols['LONG']],
                                        name,
                                        confirmed)



conn.commit()
conn.close()
