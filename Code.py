import RPi.GPIO as GPIO
import smbus
import time
import SDL_DS1307
from datetime import datetime
import requests
import json
#Datenbanken importieren
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.OUT)
 pwm = GPIO.PWM(12, 50)
#GPIOS einstellen
try:
	Response = requests.get("http://api.openweathermap.org/data/2.5/weather?id=7287641&appid=02bc5bbbcfc34f0f401e96341d110cf7")
	WeatherData = Response.json()
	warm = format(WeatherData["main"]["temp"])
	windgeschwindigkeit = format(WeatherData["wind"]["speed"])
	wolken = format(WeatherData["clouds"]["all"]) 

	wolkenwarm = int(wolken)
	warmwarm = int(float(warm))
	windgeschwindigkeitwarm = int(float(windgeschwindigkeit))
	#Openweathermap Wetter abfragen und Ausgabewert in integer
except:
	warmwarm = 270
	wolkenwarm = 20
	windgeschwindigkeitwarm = 2
	#Wenn Internet nicht funktioniert werden diese Werte den Variablen zugeordnet

def readTime():
	try:
		ds1307 = SDL_DS1307.SDL_DS1307(1, 0x68)
		return ds1307.read_datetime()
		#Zeit abfragen
	except:
		return datetime.utcnow()
		#Falls Sensor nicht geht von Raspberry direkt abfragen

timestamp = readTime()
print(timestamp.hour)
time.sleep(1)
zit = timestamp.hour + 2
print(zit)
#Wegen eines Zeitzonenfehler des Sensors mussten zwei Stunden dazu gezaehlt werden
def read(control):
	bus = smbus.SMBus(1)
	adresse = 0x48
	write = bus.write_byte_data(adresse, control, 0)
	read = bus.read_byte(adresse)
	return read
	#Temp und Licht Sensor abfragen
if True:
	licht = read(0x41)
	temperatur = read(0x42)
	poti = read(0x00)
	if temperatur <= 160 or warmwarm >=298: 
		GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
		time.sleep(1)
		pwm.start(2.5)
		print(temperatur)
		pwm.ChangeDutyCycle(7.5)
		time.sleep(1)
		GPIO.output(16, GPIO.HIGH)
		#Dach wird bei zu warmen Temperaturen geöffnet
	else:
		GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
		time.sleep(1)
		pwm.start(2.5)
		print("4", temperatur)
		pwm.ChangeDutyCycle(2.5)
		time.sleep(1)
		GPIO.output(16, GPIO.HIGH)
		#Dach wird bei zu kalten Temperaturen geschlossen

def water():
	value = 0
	for i in range(10):
		value += GPIO.input(10)
		#Feuchtigkeitssensor wird zehn Mal abgefragt um Messfehler zu verhindern
	if value == 10 and licht <= 100 or 4 <= zit <= 5 or 22 <= zit <= 23:
	#Wasser wird gegeben wenn Boden trocken und Himmel nicht bewölkt (wenn lichtwert hoch ist dann ist es bewölkt) ODER Zeit zwischen 4 und 5 Uhr ODER Zeit zwischen 22 und 23 Uhr
	# Mit den fixen Zeiten wird sichergestellt dass Feld auch an bewölkten Tagen und wenn der Boden etwas feucht ist wasser kriegt, dann aber nur minimale Wassermenge
		print(value, licht)
		GPIO.setup(10, GPIO.OUT, initial=GPIO.LOW)
		time.sleep(11)
		GPIO.output(10, GPIO.HIGH)
		#Pumpe anstellen und nach 11 Sekunden ausstellen
	else:
		print("2", value, licht)
		#Pumpe nicht anstellen

water()

if wolkenwarm >= 80:
	print("zu", wolkenwarm)
	GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
	time.sleep(1)
	pwm.start(2.5)
	pwm.ChangeDutyCycle(2.5)
	time.sleep(2)
	GPIO.output(16, GPIO.HIGH)
	#Bei zu starker Bewoelkung (Mehr als 80 Prozent Bewölkung) wird Gewaechshausdach geschlossen um Schaeden an Technik bei Regen zu verhindern
else:
	print("auf", wolkenwarm)
	#Bei geringer Bewoelkung bleibt Dach offen

time.sleep(3)

if windgeschwindigkeitwarm >= 10:
	print("zu", windgeschwindigkeitwarm)
	GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
	time.sleep(1)
	pwm.start(2.5)
	pwm.ChangeDutyCycle(2.5)
	time.sleep(2)
	GPIO.output(16, GPIO.HIGH)
	#Bei hoher Windgeschwindigkeit von mehr als 10 Meter pro Sekunde wird Dach geschlossen um Schaeden an Technik zu verhindern
else:
	print("auf", windgeschwindigkeitwarm)
	#Bei tiefer Windgeschwindigkeit bleibt Dach offen

	




	