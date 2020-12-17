import datetime
import time
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115()
adc_gain = 1

#read temp and humidity
import Adafruit_DHT
dht_sensor = Adafruit_DHT.DHT11
dht_pin = 17

#read bme value
import smbus
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte

DEVICE = 0x76 # Default device I2C address


bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
  result = data[index]
  if result > 127:
    result -= 256
  return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
  result =  data[index] & 0xFF
  return result

def readBME280ID(addr=DEVICE):
  # Chip ID Register Address
  REG_ID     = 0xD0
  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  return (chip_id, chip_version)

def readBME280All(addr=DEVICE):
  # Register Addresses
  REG_DATA = 0xF7
  REG_CONTROL = 0xF4
  REG_CONFIG  = 0xF5

  REG_CONTROL_HUM = 0xF2
  REG_HUM_MSB = 0xFD
  REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
  OVERSAMPLE_TEMP = 2
  OVERSAMPLE_PRES = 2
  MODE = 1

  # Oversample setting for humidity register - page 26
  OVERSAMPLE_HUM = 2
  bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

  control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
  bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
  cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
  cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
  cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

  # Convert byte data to word values
  dig_T1 = getUShort(cal1, 0)
  dig_T2 = getShort(cal1, 2)
  dig_T3 = getShort(cal1, 4)

  dig_P1 = getUShort(cal1, 6)
  dig_P2 = getShort(cal1, 8)
  dig_P3 = getShort(cal1, 10)
  dig_P4 = getShort(cal1, 12)
  dig_P5 = getShort(cal1, 14)
  dig_P6 = getShort(cal1, 16)
  dig_P7 = getShort(cal1, 18)
  dig_P8 = getShort(cal1, 20)
  dig_P9 = getShort(cal1, 22)

  dig_H1 = getUChar(cal2, 0)
  dig_H2 = getShort(cal3, 0)
  dig_H3 = getUChar(cal3, 2)

  dig_H4 = getChar(cal3, 3)
  dig_H4 = (dig_H4 << 24) >> 20
  dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

  dig_H5 = getChar(cal3, 5)
  dig_H5 = (dig_H5 << 24) >> 20
  dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

  dig_H6 = getChar(cal3, 6)

  # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
  wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
  time.sleep(wait_time/1000)  # Wait the required time  

  # Read temperature/pressure/humidity
  data = bus.read_i2c_block_data(addr, REG_DATA, 8)
  pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
  hum_raw = (data[6] << 8) | data[7]

  #Refine temperature
  var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
  var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
  t_fine = var1+var2
  temperature = float(((t_fine * 5) + 128) >> 8);

  # Refine pressure and adjust for temperature
  var1 = t_fine / 2.0 - 64000.0
  var2 = var1 * var1 * dig_P6 / 32768.0
  var2 = var2 + var1 * dig_P5 * 2.0
  var2 = var2 / 4.0 + dig_P4 * 65536.0
  var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
  var1 = (1.0 + var1 / 32768.0) * dig_P1
  if var1 == 0:
    pressure=0
  else:
    pressure = 1048576.0 - pres_raw
    pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
    var1 = dig_P9 * pressure * pressure / 2147483648.0
    var2 = pressure * dig_P8 / 32768.0
    pressure = pressure + (var1 + var2 + dig_P7) / 16.0

  # Refine humidity
  humidity = t_fine - 76800.0
  humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
  humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
  if humidity > 100:
    humidity = 100
  elif humidity < 0:
    humidity = 0

  return temperature/100.0,pressure/100.0,humidity

#read dust value
import RPi.GPIO as IO

#hour = datetime.datetime.now().strftime('%H')
hour = 0
while(True):
    if(hour != datetime.datetime.now().strftime('%H')):
        hour = datetime.datetime.now().strftime('%H')
        print(  str(    datetime.datetime.now().strftime('%Y%m%d%H')))

        dateAndTime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n"
        
        gas1_String = "MQ_5     = " + str(round((adc.read_adc(0, gain=adc_gain) / 65535) * 100 )) + "%\n"
        gas2_String = "MQ_9     = " + str(round((adc.read_adc(1, gain=adc_gain) / 65535) * 100 )) + "%\n"
        gas3_String = "MQ_135   = " + str(round((adc.read_adc(2, gain=adc_gain) / 65535) * 100 )) + "%\n"

        dht_humidity, dht_temperature = Adafruit_DHT.read_retry(dht_sensor,dht_pin)
        dht_humidity       = "Humidity = " + str(round(dht_humidity)) + "%\n"
        dht_temperature    = "Temp     = " + str(round(dht_temperature)) + "*C\n"

        _, bme_pressure, _ = readBME280All()
        bme_pressure       = "Pressure = " + str(round(bme_pressure)) + "hPa\n"

        #read dust level
        IO.setmode(IO.BOARD)
        IO.setwarnings(False)
        IO.setup(40,IO.OUT)
        IO.output(40,0)  
        time.sleep(0.28)  #sampling time
        
        #convert adc value to calcVoltage
        calcVoltage = adc.read_adc(3, gain=adc_gain) * (5.0 / 65535)
        
        # linear eqaution taken from http://www.howmuchsnow.com/arduino/airquality/
        dustDensity = 170 * calcVoltage - 0.1
        dust_level = "Dust     = " + str(round(dustDensity,2)) + "ug/m3\n"
        time.sleep(0.04)  #delta time
        IO.output(40,1)
        time.sleep(0.9680)#sleep time
        
        fileName = "/home/pi/Desktop/dataFolder/" + datetime.datetime.now().strftime('%Y%m%d%H') + ".txt"
        file1 = open( fileName ,"w")
        text = [dateAndTime,gas1_String,gas2_String,gas3_String,dht_humidity,dht_temperature,bme_pressure,dust_level]
        print(text)
        file1.writelines(text)
        file1.close()

if __name__=="__main__":
   main()
