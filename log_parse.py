import datetime
import os
import time
import csv
#import os.path


#todo correct for time zone difference . FLdigi and PITS use Zulu time !!

#log_path = r"C:\Users\ward\dl-fldigi.files\"
log_path = r"C:/Users/ward/dl-fldigi.files/"

headings = ['callsign',
            'Counter',
            'time',
            'Latitude',
            'Longitude',
            'Altitude',
            'HorizontalSpeed',
            'Heading',
            'Satellites',
            'Temperature',
            'BatteryVoltage',
            'BatteryCurrent'
            ]

def get_log_name(fname='fldigi'):
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")
    return fname+today+'.log'

def get_last_lines(file):
    with open(file, "rb") as f:
        #first = f.readline()  # Read the first line.
        f.seek(-2, os.SEEK_END)  # Jump to the second last byte.
        while f.read(1) != b"\n":  # Until EOL is found...
            f.seek(-3, os.SEEK_CUR)
#            f.seek(-2, os.SEEK_CUR)  # ...jump back the read byte plus one more.
        last = f.readline()  # Read last line.
    return last

def extract_sentance(line, sep='$$'):
    try:
        if sep in last_line:
            extract = last_line.split('$$', 50)
            #print('Extracted', extract[1])
            return extract[1]
        elif sep not in last_line:
            #print('not found')
            pass
    except Exception as e:
        print(e)
        pass
    return

def make_list(extracted):
    try:
        if not extracted == None:
            made = extracted.split(',')
        #made = extracted.Split(',').ToList()
            return made

    except Exception as e:
        print(e)
        pass

def write_file(list, fname='sentancelog',headings=headings):
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")

    # TODO make method for constructing the full path with file type exention
    full_name = fname+today+'.csv'
    full_path = log_path+full_name

    try:
        if os.path.isfile(full_path):
            with open(full_path, 'a', newline='') as f:
                wr = csv.writer(f, quoting=csv.QUOTE_ALL)
                wr.writerow(list)
            return

        with open(full_path, 'w', newline='') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(headings)
            return

    except Exception as e:
        print('Trying to write the log.csv file')
        print(e)
        pass

def check_list(s, labels=headings):

#callsign
    try:
        if not isinstance(s[0], str):
            s[0] = 'garbled'
    except Exception as e:
        s.append('nan')
        #pass
#Counter
    try:
        s[1] = int(s[1])
        if not isinstance(s[1], str):
            Counter = 'garbled'
    except:
        s.append('nan')
       # pass
#time
    # if time not in range(00:00:00,12:59:59):
    #     time = 'nan'
#Latitude
    try:
        s[3] = float(s[3])

        if not 0 <= s[3] <= 90:
            #if s[3] not in range(0,90):
            s[3] = 'nan'
    except:
        s.append('nan')
      #  pass
#Longitude
    try:
        s[4] = float(s[4])
        if not 0 <= s[4] <= 90:
            s[4] = 'nan'
    except:
        s.append('nan')
    #    pass
#Altitude
    try:
        s[5] = int(s[5])
        if s[5] not in range(-1000,50000):
            s[5] = 'nan'
    except:
        s.append('nan')
      #  pass
#HorizontalSpeed
    try:
        s[6] = float(s[6])
        if not 0 <= s[6] <= 100000:
            s[6] = 'nan'
    except:
        s.append('nan')
      #  pass
#Heading
    try:
        s[7] = int(s[7])
        if s[7] not in range(0,360):
            s[7] = 'nan'
    except:
        s.append('nan')
      #  pass

#Satellites
    try:
        s[8] = int(s[8])
        if s[8] not in range(0, 15):
            s[8] = 'nan'
    except:
        s.append('nan')
   #     pass
#Temperature
    try:
        s[9] = float(s[9])
        if not -270 <= s[9] <= 200:
            s[9] = 'nan'
    except:
        s.append('nan')
      #  pass
#BatteryVoltage
    try:
        s[10] = float(s[10])
        if not 0 <= s[9] <= 36:
            s[10] = 'nan'
    except:
        s.append('nan')
      #  pass
#BatteryCurrent
    try:
        s[11] = float(s[11])
        if not 0 <= s[9] <= 3000:
            s[11] = 'nan'
    except:
            s.append('nan')
     #       pass

    checked = []
    for d in range(0,11):
        checked.append(s[d])
    return checked

if __name__ == '__main__':
    print(log_path)
    print(get_log_name())

    while True:
        full_path  = log_path+get_log_name()

        last_lines = get_last_lines(full_path)
        last_line = last_lines.decode('utf-8')
        #print(last_line)

        extract = extract_sentance(last_line)
        #print(extract)

        if not extract == None:
            sentance = make_list(extract)
            #print('sentance = ', sentance)
            sentance_checked = check_list(sentance)

            print('checked   =', sentance_checked)
            write_file(sentance_checked)

        time.sleep(5)



