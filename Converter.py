import os
import sys
import time
import csv
from datetime import datetime, timedelta
from time import strftime, gmtime

working_dir = os.getcwd()


def replace(myDict):
    for key, value in myDict.items():
        for dKey, dValue in value.items():
            temp = dValue
            if "&" in dValue:
                temp = temp.replace("&", "&amp;")
            # if "'" in dValue:
            #     temp = temp.replace("'", "&apos;")
            if '"' in dValue:
                temp = temp.replace('"', "&quot;")
            if "<" in dValue:
                temp = temp.replace("&", "&lt;")
            if ">" in dValue:
                temp = temp.replace("&", "&gt;")
            value[dKey] = temp
    return myDict


def display_output(to_display, hold_time):
    print(f'''{to_display}''')
    time.sleep(hold_time)


def create_files_and_folders(list_of_dir):
    folders = ["CSV_to_convert", "converted_XML"]
    for x in folders:
        if x not in list_of_dir:
            os.mkdir(x)
            display_output(x, .5)
    if "format.txt" not in list_of_dir:
        format_file = open(f'''format.txt''', "w+")
        format_file.write("#Copy files to CSV_to_convert folder, add format here, only then file is converted\n")
        format_file.write(
            "#Converted files will be placed in converted_XML folder , add format here, only then file is converted\n")
        format_file.write("# lines starting with '#' are ignored rest are read as input csv file\n")
        format_file.write("# use bar'|' as separator without spaces\n")
        format_file.write("# Example\n")
        format_file.write("#test.csv|test.xml|+0600|test_header_text\n")
        format_file.close()
        display_output("format.txt", .5)
    return


def read_format_file(format_file):
    csv_dict = {}
    with open(working_dir + "\\" + "format.txt") as f:
        lines = f.readlines()
        for line in lines:
            if not (line.startswith("#") or line.startswith('\n')):
                line = line.rstrip().split('|')
                csv_dict[f'''{line[1]}'''] = {'csv': f'''{line[0]}'''.strip(),
                                              'xml': f'''{line[1]}'''.strip(),
                                              'timeZone': f'''{line[2]}'''.strip(),
                                              'id': f'''{line[3]}'''.strip()}

    return csv_dict


def read_csv_file(csv_file, csvElements):
    line_number = 0
    os.chdir(os.sep.join([working_dir, "CSV_to_convert"]))
    with open(f'''{csv_file}''') as in_file:
        reader = csv.reader(in_file, delimiter=',')
        for _ in reader:
            dictIn = {'date': _[0].replace('\\', ''),
                      'time': _[1].replace('\\', ''),
                      'duration': _[2].replace('\\', ''),
                      'title': _[3].replace('\\', ''),
                      "desc": _[4].replace('\\', '')}
            csvElements.update({line_number: dictIn})
            line_number += 1
    os.chdir(working_dir)
    del csvElements[0]
    return csvElements


def write_xml_file(xml_format, replaced_csvElements):
    os.chdir(os.sep.join([working_dir, "converted_XML"]))
    inputFile = xml_format["csv"]
    outputFile = xml_format["xml"]
    channel_name = xml_format["id"]
    timeZone = xml_format["timeZone"]
    program_id = 0

    top = f'''<?xml version="1.0" encoding="UTF-8"?>
<tv>
	<channel id="{channel_name}">
		<display-name lang="en">{channel_name}</display-name>
	</channel>'''
    program_items = []

    for lines in replaced_csvElements:
        program_id += 1

        startDate = datetime.strptime(replaced_csvElements[lines]['date'], '%d/%m/%Y').date()
        startDateString = str(startDate).replace('-', '')
        startTime = datetime.strptime(replaced_csvElements[lines]['time'], '%H:%M:%S').time()
        startTimeString = str(startTime).replace(':', '')
        start = ''.join((startDateString, startTimeString, ' ', timeZone))
        try:
            duration = datetime.strptime(replaced_csvElements[lines]['duration'], '%H:%M').time()
        except:
            pass
        stopTime = timedelta(hours=startTime.hour + duration.hour, minutes=startTime.minute + duration.minute)
        if stopTime.days == 1:
            stopTimeString = strftime("%H:%M:%S", gmtime(stopTime.seconds)).replace(':', '')
        else:
            stopTimeString = str(timedelta(seconds=stopTime.seconds)).replace(':', '')
        if len(stopTimeString) == 5:
            stopTimeString = '0' + stopTimeString
        stopDate = startDate + timedelta(days=stopTime.days)
        stopDateString = str(stopDate).replace('-', '')
        stop = ''.join((stopDateString, stopTimeString, ' ', timeZone))

        program_items.append(
            f'''	<programme id="{program_id}" channel="{channel_name}" start="{start}" stop="{stop}">
		<title>{replaced_csvElements[lines]['title']}</title>
		<desc>{replaced_csvElements[lines]['desc']}</desc>
	</programme>''')

        bottom = '''</tv>'''

    with open(outputFile, 'w+', encoding='utf_8') as out_file:
        out_file.write(f'''{top}\n''')
        for _ in program_items:
            out_file.write(f'''{_}\n''')
        out_file.write(f'''{bottom}\n''')

    os.chdir(working_dir)


def program():
    csvElements = {}
    list_of_dir = os.listdir()
    create_files_and_folders(list_of_dir)
    converted_files_list = []
    display_output("Developed by Harihar Thapa\nREAD [format.txt] file for conversion detail\n", 2)
    # read format.txt
    try:
        csv_list_format = read_format_file("format.txt")
    except Exception as e:
        display_output(e, 2)

    # read csv file if it is in format.txt and in CSV_to_convert folder
    os.chdir(os.sep.join([working_dir, "CSV_to_convert"]))
    csv_list_folder = os.listdir()
    for _ in csv_list_format.keys():
        csv_file = csv_list_format[_]['csv']
        if csv_file in csv_list_folder:
            try:
                csvElements = read_csv_file(csv_file, csvElements)
                replaced_csvElements = replace(csvElements)
                write_xml_file(csv_list_format[_], replaced_csvElements)
                replaced_csvElements.clear()
                csvElements.clear()
            except Exception as e:
                display_output(e, 2)
        converted_files_list.append(_)
    if converted_files_list:
        converted_files_count = 1
        for _ in converted_files_list:
            display_output(f'''{converted_files_count} {_}''', 0)
            converted_files_count += 1
        display_output(f'''------------- {len(converted_files_list)} csv's converted--------------''', 5)
    else:
        display_output("0 FILES Converted\nRe-READ and Adjust FORMAT", 5)


if __name__ == '__main__':
    program()
