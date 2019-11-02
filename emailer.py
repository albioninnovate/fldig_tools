# on run this program sends an email to the
# given address containg the IP addres
# in the meassage body and subject line.
# thiscode is based on that found here:
# http://cagewebdev.com/index.php/raspberry-pi-sending-emails-on-boot/
# http://elinux.org/RPi_Email_IP_On_Boot_Debian
# @author: Jeremy Blythe
# http://jeremyblythe.blogspot.co.uk/2013/03/raspberry-pi-system-monitor-embedded-on.html


# primarly utility is to send the IP address and other informaion at boot so that
# a SSH connection can be established on a new network

# To run the code at start up,  in the Rasbian distro
# place a call for execution in etc/rc.local directory
# the code for the rc.local fime is:
# sleep 60  #to allow time for the IP address to be established very important in case of WiIF
# _IP=$(hostname -I) || true
# if [ "$_IP" ]; then
#   printf "My IP address is %s\n" "$_IP"
#   python /home/pi/Code/startup_mailer.py
# fi


import subprocess
import smtplib
import socket
import os
from email.mime.text import MIMEText
import datetime
import time
import pickle

# Change to your own account information

to = 'wardhills@gmail.com'
gmail_user = 'your_email@gmail.com'
gmail_password = 'Your_password'
smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_password)
today = datetime.date.today()


# Determine the IP Address

def get_ipaddr():
    try:
        arg = 'ip route list'
        p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
        data = p.communicate()
        split_data = data[0].split()
        return (split_data[split_data.index('src') + 1])
    except:
        return 0


# report time now
from time import gmtime, strftime

time_now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())


def get_ram():
    "Returns a tuple (total ram, available ram) in megabytes. See www.linuxatemyram.com"
    try:
        s = subprocess.check_output(["free", "-m"])
        lines = s.split('\n')
        return (int(lines[1].split()[1]), int(lines[2].split()[3]))
    except:
        return 0


def get_process_count():
    "Returns the number of processes"
    try:
        s = subprocess.check_output(["ps", "-e"])
        return len(s.split('\n'))
    except:
        return 0


def get_up_stats():
    "Returns a tuple (uptime, 5 min load average)"
    try:
        s = subprocess.check_output(["uptime"])
        load_split = s.split('load average: ')
        load_five = float(load_split[1].split(',')[1])
        up = load_split[0]
        up_pos = up.rfind(',', 0, len(up) - 4)
        up = up[:up_pos].split('up ')[1]
        return (up, load_five)
    except:
        return ('', 0)


def get_connections():
    "Returns the number of network connections"
    try:
        s = subprocess.check_output(["netstat", "-tun"])
        return len([x for x in s.split() if x == 'ESTABLISHED'])
    except:
        return 0


def get_temperature():
    "Returns the temperature in degrees C"
    try:
        s = subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"])
        return float(s.split('=')[1][:-3])
    except:
        return 0


# The information to report
ip_rpt = 'IP address: ' + str(get_ipaddr())
temp_rpt = 'Temperature in C: ' + str(get_temperature())
conn_rpt = 'Nr. of connections: ' + str(get_connections())
ram_rpt = 'Free RAM: ' + str(get_ram()[1]) + ' (' + str(get_ram()[0]) + ')'
proc_rpt = 'Nr. of processes: ' + str(get_process_count())
uptime_rpt = 'Up time: ' + get_up_stats()[0]

# send email

mail_body = 'Hello Dr Hills.\n \n It is now: ' + time_now + '\n ' + ip_rpt + '\n' + ram_rpt + '\n ' + proc_rpt + '\n' + uptime_rpt + '\n' + conn_rpt + '\n' + temp_rpt + '\n'
msg = MIMEText(mail_body)
msg['Subject'] = 'RasPI @ ' + ip_rpt + ' started up on %s' % today.strftime('%b %d %Y')
msg['From'] = gmail_user
msg['To'] = to
smtpserver.sendmail(gmail_user, [to], msg.as_string())
smtpserver.quit()

# WRITE FILE
# this section writes a file containing the above information.  The filename is timestamped
# the file can be updated in another programme triggered in crontab)
# The file is writes to a directory /home/pi/sysstat_file/

# Create file .csv with time stamp name and that contains the curretnt System Stats at statup

time_stmp = strftime("%Y%m%d%H%M%S", gmtime())

# the file name will be "YEARMODATETIME.csv"

file_name = time_stmp + '.csv'

# data is a listing of the itmes to be writen to the file
# data = time_now,ip_rpt,ram_rpt,proc_rpt,uptime_rpt,conn_rpt,temp_rpt,cpu_rpt

# data_structure = "Year" , "Month" , "Day", "Hour", "Minute", "Second", "Time Stamp", "Up Time", "IP Address", "CPU Temperature", "Connections", "RAM", "Processes"
data = strftime("%Y,%m,%d,%H,%M,%S", gmtime()), time_stmp, get_up_stats()[0], str(get_ipaddr()), str(
    get_temperature()), str(get_connections()), str(get_ram()[1]), str(get_process_count())

f = open('/home/pi/sysstat_file/' + file_name, 'a')
# f.write(data_structure+"\n")
for item in data:
    f.write(str(item) + ",")
f.write("\n")
f.close()

# write a Pickle file containing the filename with timestamp and the file path

file_list = [file_name]

f = open('flie_list.pickle', 'w')
pickle.dump(file_list, f)
f.close()