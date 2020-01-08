import sys
import glob
import serial
import socket
import  datetime

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class gps:

    def raw_to_nmea(self,lat,lng):
        lat = float(lat)
        lng = float(lng)
        lata = abs(lat)
        latd = int(str(lata)[:str(lata).find('.')])
        latm = (lata - latd) * 60
        if(lat>0):
            lath="N"
        else:
            lath="S"
        lnga = abs(lng)
        lngd = int(str(lnga)[:str(lnga).find('.')])
        lngm = (lnga - lngd) * 60
        if(lng>0):
            lngh = "E"
        else:
            lngh = "W"



        latm = float(str(latm)[:str(latm).find('.')+6])
        lngm = float(str(lngm)[:str(lngm).find('.') + 6])

        nmea = '$GPGLL,'

        if(latd<=10):
            nmea+='0'+str(latd)
        else:
            nmea+=str(latd)

        if(latm<=10):
            nmea += '0' + str(latm)
        else:
            nmea +=str(latm)

        nmea+=","
        nmea+=lath
        nmea += ","
        nmea += "0"
        if(lngd<=10):
            nmea+='0'+str(lngd)
        else:
            nmea+=str(lngd)
        if(lngd<=10):
            nmea+='0'+str(lngm)
        else:
            nmea+=str(lngm)
        nmea +=","
        nmea+=lngh
        nmea += ','+ str(self.gettime()) +'.00,A,A*51'
        return nmea.encode()

    def lat_lon_conversion(self,rawstring):
         pos = 2
         rawstring = str(rawstring)
         lat = rawstring.find("LAT")
         lon = rawstring.find("LON")
         latstring = (rawstring[lat+3:lon])
         lonstring = (rawstring[lon + 3:len(rawstring)])
         return (self.raw_to_nmea(latstring,lonstring).encode(),pos)

    def gettime(self):
        d = str(datetime.datetime.utcnow())
        d = d[d.find(" "):d.find(".")]
        d= d.replace(":","")
        return d

    def send_over_udp(self,rawstring,ip):
        try:
            ind = self.check_name_list(rawstring)
            nmea_message,pos = self.lat_lon_conversion(rawstring)
            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

            port =2000+self.list_names.index(ind)
            sock.sendto(nmea_message, (ip, port)) #port is 2000 plus position in the list
            print("writing:",nmea_message.decode("UTF-8")," on:",ip," port:",port)
        except:
            print("No lock")

    def check_name_list(self,string_to_check):
        string_to_check = string_to_check[1:]
        string_to_check = string_to_check[:string_to_check.find("LAT")]
        number = int(string_to_check)
        if not number in self.list_names:
            self.list_names.append(number)
        return number

    def publish_data(self,serial_port,ip):
        ser = serial.Serial(serial_port, 9600)  # open serial port
        is_valid = 0
        str_byte = ""
        while True:
            seriial_string = ser.read(1)
            if (seriial_string == b'%'):
                str_ser = bytearray(b'')
                term = b''
                counter = 0
                while not term is b'$':
                    counter += 1
                    if (counter > 50):
                        break
                    term = ser.read(1)
                    if(term == b'$'):
                        break
                    str_ser += term
                str_byte = str_ser.decode('utf-8')
                str_byte = str_byte[1:len(str_byte) - 1]
                print(str_byte)
                self.check_name_list(str_byte)
                self.send_over_udp(str_byte,ip)

if __name__ == '__main__':
    x = gps()
    print("Available Ports:")
    for s in serial_ports():
        print(s)
    desc = input("Do you want to use the auto-ip-finder ? (yes/no)")

    if(desc=="yes"):
        ip = socket.gethostbyname(socket.gethostname())
    else:
        ip =input("IP: ")

    port = input("standard port ? (yes/no")

    if(port =="yes"):
        serial_port = "com5"
    else:
        serial_port = input("Plase give the Serial Port of the Base Station: ")

    print("Used IP:", ip)
    print("Listening on ", serial_port)
    x.gettime()
    x.publish_data(serial_port, ip)
