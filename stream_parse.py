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



##Code below from https://github.com/PiInTheSky/LCARS (with thanks)

def ProcessdlfldigiLine(line):
    # $BUZZ,483,10:04:27,51.95022,-2.54435,00190,5*6856
    #print('line received - ', line)

    field_list = line.split(",")

    #Payload = field_list[0][1:]
    print(field_list)

    targ_sentance = field_list

    targ_pos = [
        float(targ_sentance[3]),
        float(targ_sentance[4]),
        float(targ_sentance[5]),
        targ_sentance[0]
    ]

    calc_vector(targ_pos, my_pos)


    # PayloadIndex = FindFreePayload(Payload)
    #
    # HABStatii[PayloadIndex]['payload'] = Payload
    # if j['time'] != HABStatii[PayloadIndex]['time']:
    #     HABStatii[PayloadIndex]['lastupdate'] = int(time.time())
    #     Sources[2]['lastupdate'] = int(time.time())
    # HABStatii[PayloadIndex]['time'] = field_list[2]
    # HABStatii[PayloadIndex]['lat'] = float(field_list[3])
    # HABStatii[PayloadIndex]['lon'] = float(field_list[4])
    # HABStatii[PayloadIndex]['alt'] = float(field_list[5])
    # HABStatii[PayloadIndex]['rate'] = 0
    # HABStatii[PayloadIndex]['updated'] = 1

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

        print("Connected to dl-fldigi")
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


    #calc_vector(targ_pos, my_pos)


    # print(log_path)
    # print(get_log_name())

    # while True:
    #     full_path  = log_path+get_log_name()
    #
    #     last_lines = get_last_lines(full_path)
    #     last_line = last_lines.decode('utf-8')
    #     #print(last_line)
    #
    #     extract = extract_sentance(last_line)
    #     #print(extract)
    #
    #     if not extract == None:
    #         sentance = make_list(extract)
    #         #print('sentance = ', sentance)
    #         sentance_checked = check_list(sentance)
    #
    #         print('checked   =', sentance_checked)
    #         write_file(sentance_checked)
    #
    #     time.sleep(5)
