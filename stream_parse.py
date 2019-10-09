import datetime
import os
import time
import csv
import socket
#import os.path
from geonum import GeoPoint


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


##Code below from https://github.com/PiInTheSky/LCARS (with thanks)

def ProcessdlfldigiLine(line):
    field_list = line.split(",")

    print(field_list)

    targ_sentance = field_list

    targ_pos = [
        float(targ_sentance[3]),
        float(targ_sentance[4]),
        float(targ_sentance[5]),
        targ_sentance[0]
    ]
    
    calc_vector(targ_pos, my_pos)

def Processdlfldigi(s):
    line = ''
    while 1:
        reply = s.recv(1)
        if reply:
            value = reply[0]
            if value == 9:
                pass
            elif value == 10:
                if line != '':
                    ProcessdlfldigiLine(line)
                    line = ''
            elif (value >= 32) and (value < 128):
                temp = chr(reply[0])
                if temp == '$':
                    line = temp
                elif line != '':
                    line = line + temp

        else:
            time.sleep(1)


def dodlfldigi(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((host, port))

        #print("Connected to dl-fldigi")
        # Sources[2]['connected'] = 1

        Processdlfldigi(s)

        print(x)

        s.close()

    except:
        # Sources[2]['connected'] = 0
        pass


def dlfldigi_thread():
    host = "localhost"
    port = 7322

    print("Trying to connect to dl-fldigi at " + host + ":" + str(port))

    while 1:
        dodlfldigi(host, port)

def calc_vector(targ_pos, my_pos):
    #  tar_pos _ lat_B, lon_B, alt_B , 'name'
    print( 'calc vector')
    print(targ_pos[0])

   # p1 = GeoPoint(lat=lat_A, lon=lon_A, altitude=alt_A, name=name_A)
    p1 = GeoPoint(targ_pos[0],targ_pos[1],targ_pos[2],targ_pos[3])
    print(p1)
    #p2 = GeoPoint(lat=lat_B, lon=lon_B, altitude=alt_B, name=name_B)
    p2 = GeoPoint(my_pos[0],my_pos[1],my_pos[2],my_pos[3])

    connection_vector = p2 - p1

    print('connection_vector' , connection_vector)

    GeonumDistance = connection_vector.magnitude
    GeonumDistance = float("{0:.4f}".format(GeonumDistance))

    print("Geonum:", GeonumDistance, "km")
    return  GeonumDistance


if __name__ == '__main__':

    global targ_sentance
    global my_pos

    my_pos = [52.2265, 0.0901, 24, 'Albion House']    #lat_B, lon_B, alt_B , 'name'

    dlfldigi_thread()
    dodlfldigi()

    targ_pos = [
        targ_sentance[4],
        targ_sentance[5],
        targ_sentance[6],
        targ_sentance[0]
        ]
    print(targ_pos)