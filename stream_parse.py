import datetime
import os
import time
import csv
import socket
#import os.path
from geonum import GeoPoint
import sys

#todo correct for time zone difference . FLdigi and PITS use Zulu time !!

#log_path = r"C:\Users\ward\dl-fldigi.files\"
log_path = r"C:/Users/ward/dl-fldigi.files/"

# the standard data feilds sent by the PITS software
headings_PITS = ['callsign',
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
                ]

# data feilds sent by the sensors_balloon/src/sesnsors.py

data_keys =    ['gyro_x'  ,
                'gyro_y'  ,
                'gyro_z'  ,
                'accel_z' ,
                'infrared',
                'Temp.'   ,
                'timestamp'
                ]

headings= headings_PITS + data_keys
#print('headings', headings)

def write_file(list, fname='data',headings=headings,path='./'):
    """

    :param list:
    :param fname:
    :param headings:
    :param path:
    :return:
    """
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")

    # TODO make method for constructing the full path with file type exention
    full_name = fname+today+'.csv'
    full_path = path+full_name

    try:

        print('WRITING to disk')
        print(list)
        print('--')
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
    """

    :param line:
    :return:
    """

    try:
        data_list = line.split(",")
        print('data_list = ', data_list)
        #print('$'+call_sign)

        if data_list[0] == '$'+call_sign:
            time_item = data_list[2]
            time_stamp = str(data_list[-1])             # extract the last field, convet to str
            time_stamp = time_stamp.split('*')[0]       # split chars appened to by PITS software
            
            data_list.pop(0)                            # remove the strings from the list ( call sign)  
            data_list.pop(1)                            #            transmit time
            data_list.pop(-1)                           #        timestamp+appended str  
            data_list.append(float(time_stamp))     # add flast part of timestamp back into list 

            data = [float(x) for x in data_list]    # converts strings to float
              
            data.insert(0,'$'+call_sign)         # re add the str data that was removed above
            data.insert(2,time_item)               

            try:
                calc_vector(data, base_pos)
            except Exception as e:
                print('error in calc_vector')
                print(e)
                pass

            try:
                write_file(data)

            except Exception as e:
                print('error in write_file')
                print(e)
                pass

            try:
                report_status(data)

            except Exception as e:
                print('error in report_status')
                print(e)
                pass

    except Exception as e:
        print('error in ProcessdlfldigiLine')
        print(e)
        pass

def Processdlfldigi(s):
    """

    :param s:
    :return:
    """
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
    """

    :param host:
    :param port:
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((host, port))

        Processdlfldigi(s)

        print(x)

        s.close()

    except Exception as e:
        print('Error in dodlfldigi')
        print(e)
        pass


def dlfldigi_thread():
    """

    :return:
    """
    host = "localhost"
    port = 7322

    print("Trying to connect to dl-fldigi at " + host + ":" + str(port))

    while 1:
        dodlfldigi(host, port)

def calc_vector(targ_sentance, base_pos):
    """

    :param targ_sentance:
        #targ_sentance[3] - Lat
        #targ_sentance[4] - Lon
        #targ_sentance[5] - Alt
    :param base_pos:
    :return:
    """
    try:
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
        #print('\n=Starts=======================================================')
        print('=====Received at: ',datetime.datetime.now(),'===================')
        print('Target: ', targ_pos[3],' , lat/lon : ',targ_pos[0], ' / ',targ_pos[1], 'Alt : ',targ_pos[2])  
        #print('\n')
        print('connection_vector' , connection_vector)

        GeonumDistance = connection_vector.magnitude
        #GeonumDistance = float("{0:.4f}".format(GeonumDistance))
        
        #print("Geonum:", GeonumDistance, "km")
        print("--")
        return  GeonumDistance
    
    except Exception as e:
        print('error in calc_vector')
        print(e)
        pass

def report_status(data, headings=headings):
    """

    :param data:
    :param headings:
    :return:
    """
    d = dict(zip(headings, data))

    print("STATUS:")

    print('Horizontal Speed, heading : ',
          d['HorizontalSpeed'],'m/s',
          d['Heading'],'deg'
          )

    print('Acceleration :            ',
          # d['accel_x'],
          # d['accel_y'],
          '  Z:', d['accel_z'], 'm/s2' 
          )

    # print ('Magnetic field (x,y,z) gauss (??UNITS??) :',
    #        d['mag_x'],
    #        d['mag_y'],
    #        d['mag_Z'],
    #       '\n')
    
    print ('Gyro :                    ',
           '  X:',d['gyro_x'],
           '  Y:',d['gyro_y'],
           '  Z:',d['gyro_z'],'rad/s'
          )

    print('infrared :                  ',
          d['infrared'],
          # d['Humid'],
         )

    print('Temp (external) :           ',
          d['Temp.'],'C'
          # d['Humid'],
          )
    print('Temp. (internal) :          ',
          d['Temperature'],'C',
          )

    print('Battery :                   ',
          d['BatteryVoltage'],'V',
          d['BatteryCurrent'],'mA',
          )

    print('TimeStamp (time at target) :', datetime.datetime.fromtimestamp(d['timestamp']).isoformat())
    print('================================================================ends===\n')

if __name__ == '__main__':
    global call_sign
    call_sign = 'CST'
    #global targ_pos

    global base_pos
    base_pos = [52.2265, 0.1158, 11,'Green']  # lat_B, lon_B, alt_B , 'name'

    # if len(sys.argv) < 3:
    #
    #     print(' Set the base location with:\n ')
    #     print('python3 stream_parse.py  latitude  longitude  altitude  name \n')
    #     print('space between each parameter and the values in decimals\n ')
    #
    # else:
    #     base_pos = [sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[3]]

    dlfldigi_thread()
    dodlfldigi()
