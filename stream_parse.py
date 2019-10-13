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
            'BatteryCurrent',
            'accel_x',
            'accel_y',
            'accel_Z',
            'mag_x',
            'mag_y',
            'mag_Z',
            'G-X',
            'G-Y',
            'G-Z',
            'Temp',
            'Humid',
            'TimeStamp'
            ]

def write_file(list, fname='data',headings=headings,path='./'):
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")

    # TODO make method for constructing the full path with file type exention
    full_name = fname+today+'.csv'
    full_path = path+full_name

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

    try:
  
        data_list = line.split(",")
        #print('data_list[0] = ', data_list[0])
        #print('$'+call_sign)

        if data_list[0] == '$'+call_sign:
            time_item = data_list[2]
            time_stamp = str(data_list[-1])             # extract the last field, convet to str
            time_stamp = time_stamp.split('*')[0]       # split chars appened to by PITS software
            
            data_list.pop(0)                            # remove the strings from the list ( call sign)  
            data_list.pop(1)                            #        transmit time
            data_list.pop(-1)                           #        timestamp+appended str  
            data_list.append(float(time_stamp))         # add flast part of timestamp back into list  

            data = [float(x) for x in data_list] # converts strings to float

            data.insert(0,'$'+call_sign)         # re add the str data that was removed above
            data.insert(2,time_item)               

            calc_vector(data, base_pos)
            
            write_file(data)

            report_status(data)

    except Exception as e:
        print('error in ProcessdlfldigiLine')
        print(e)
        pass

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

    except Exception as e:
        print('Error in dodlfldigi')
        print(e)
        pass
   


def dlfldigi_thread():
    host = "localhost"
    port = 7322

    print("Trying to connect to dl-fldigi at " + host + ":" + str(port))

    while 1:
        dodlfldigi(host, port)

def calc_vector(targ_sentance, base_pos):
    try:
                                                    #targ_sentance[3] - Lat
                                                    #targ_sentance[4] - Lon
                                                    #targ_sentance[5] - Alt

        if 45 <= int(targ_sentance[3]) <= 70:       # is Lat is a reasonable number, for Europe. 
                                                    # extract the position (lat,lon alt and name)
            targ_pos = [
                float(targ_sentance[3]),
                float(targ_sentance[4]),
                float(targ_sentance[5]),
                targ_sentance[0]
                ]

        targ = GeoPoint(targ_pos[0],targ_pos[1],targ_pos[2],targ_pos[3])

        base = GeoPoint(base_pos[0],base_pos[1],base_pos[2],base_pos[3])

        connection_vector = targ - base
        print('\n=Starts=======================================================\n')
        print('Reveived at: ',datetime.datetime.now())
        print('Target: ', targ_pos[3],' , lat/lon : ',targ_pos[0], ' / ',targ_pos[1], 'Alt : ',targ_pos[2])  
        print('\n')
        print('connection_vector' , connection_vector)

        GeonumDistance = connection_vector.magnitude
        #GeonumDistance = float("{0:.4f}".format(GeonumDistance))
        
        print("Geonum:", GeonumDistance, "km")
        print("--")
        return  GeonumDistance
    
    except Exception as e:
        print('error in calc_vector')
        print(e)
        pass

def report_status(data, headings=headings):
    d = dict(zip(headings, data))
   # print(d)
    print('Horizontal (m/s, heading) :',
          d['HorizontalSpeed'],
          d['Heading'],
          '\n')
    print('Temp. (internal)', d['Temperature'],
          '\n')
    print('Battery V,mA ',
          d['BatteryVoltage'],
          d['BatteryCurrent'],
          '\n')

    print('Acceleration (x,y,z) m/s2 :',
          d['accel_x'],
          d['accel_y'],
          d['accel_Z'],
          '\n')

    print ('Magnetic field (x,y,z) gauss (??UNITS??) :',
           d['mag_x'],
           d['mag_y'],
           d['mag_Z'],
          '\n')
    
    print ('Gyro (x,y,z) rad/s  :',
           d['G-X'],
           d['G-Y'],
           d['G-Z'],
          '\n')

    print('Temp/Humid (external) :',
          d['Temp'],
          d['Humid'],
          '\n')

    print('TimeStamp (time at target) :', datetime.datetime.fromtimestamp(d['TimeStamp']).isoformat())
    print('\n================================================================ends\n')

if __name__ == '__main__':

    #global targ_sentance
    global base_pos
    global call_sign

    call_sign = 'CST'

    base_pos = [52.2265, 0.0901, 24, 'Albion House']    #lat_B, lon_B, alt_B , 'name'

    dlfldigi_thread()
    dodlfldigi()



