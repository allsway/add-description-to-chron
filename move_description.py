#!/usr/bin/python
import requests
import sys
import csv
import configparser
import logging
import xml.etree.ElementTree as ET

# Returns the API key
def get_key():
	return config.get('Params', 'apikey')

# Returns the Alma API base URL
def get_base_url():
	return config.get('Params', 'baseurl')

# Gets the item barcode 
def get_item_xml(barcode):
	item_url = get_base_url() + "items?item_barcode=" + barcode +  "&apikey=" + get_key()
	print (item_url)
	response = requests.get(item_url)
	if response.status_code != 200:
		logging.info("Item not found for item barcode: " + barcode)
		return None
	item = ET.fromstring(response.content)
	return item
	
# posts the updated item, with the new chronology information
def post_item(item_xml):
	item_url =  item_xml.attrib['link'] + "?apikey=" +  get_key()
	header = {"Content-Type": "application/xml"}
	r = requests.put(item_url,data=ET.tostring(item_xml),headers=header)
	print (r.content)
	
# parses the row in the item csv file
def parse_row(row):
	barcode = row[3]
	print(barcode)
	item_data = get_item_xml(barcode)
	for item in item_data.findall("item_data"):
		description = item.find('description').text
		print (item.find('description').text)
		enum_a = item.find('enumeration_a')
		if enum_a.text is None:
			enum_a.text = description
	post_item(item_data)
	
# Reads in file of csv files
def read_items(item_file):
	f  = open(item_file,'rt')
	try:
		reader = csv.reader(f)
		header = next(reader)
		for row in reader:
			if row[0] != 'end-of-file':
				parse_row(row)
	finally:
		f.close()


config = configparser.ConfigParser()
config.read(sys.argv[1])

logging.basicConfig(filename='status.log',level=logging.DEBUG)
items = sys.argv[2]
read_items(items)