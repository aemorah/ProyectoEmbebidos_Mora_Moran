import RPi.GPIO as GPIO
from time import*
from firebase import firebase
from wiringpi import Serial
#Proyecto Embebidos Alex Mora, Jaime Moran
#Conexion con Firebase
firebase = firebase.FirebaseApplication('https://proyectoembebidoskioskos-default-rtdb.firebaseio.com/', None)

#Conexion con Terminal Virtual
baud = 115200
ser  = Serial("/dev/serial0",baud)
sleep(0.3)

#Variables para la tarjeta RFID
btInicio = 17
btFin = 4


#Variables para el selector de monedas
bt1 = 22
bt2 = 27
ld1 = 20
ld2 = 26

#Definición de pines para el LCD
pantalla_RS = 5
pantalla_E  = 6
pantalla_D4 = 12
pantalla_D5 = 13
pantalla_D6 = 16
pantalla_D7 = 19


#Recibe la información Guardada en la tajeta
def recibir(echo = True):
 data = ""
 while True:
  input = ser.getchar()
  if echo:
   ser.putchar(input)
  if input == "\r":
   return (data)
  data += input
 sleep(0.2)
  
def printsln(menss):
 ser.puts(menss+"\r")
 sleep(0.2)

def prints(menss):
 ser.puts(menss)
 sleep(0.2)
 
#Se configuran los pines de a Raspberry Pi 3
def peripheral_setup():
 GPIO.setmode(GPIO.BCM)
 GPIO.setup(bt1, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(bt2, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(btInicio, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(btFin, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(ld1, GPIO.OUT)
 GPIO.setup(ld2, GPIO.OUT)
 GPIO.setup(pantalla_RS, GPIO.OUT)  
 GPIO.setup(pantalla_E, GPIO.OUT) 
 GPIO.setup(pantalla_D4, GPIO.OUT) 
 GPIO.setup(pantalla_D5, GPIO.OUT) 
 GPIO.setup(pantalla_D6, GPIO.OUT) 
 GPIO.setup(pantalla_D7, GPIO.OUT) 
 
 lcd_init()
 
 lcd_string("Bienvenido!!", 0x80)


 
#Funcion para inicializar la LCD
def lcd_init():
  lcd_byte(0x33,False) 
  lcd_byte(0x32,False) 
  lcd_byte(0x06,False) 
  lcd_byte(0x0C,False) 
  lcd_byte(0x28,False) 
  lcd_byte(0x01,False) 
  sleep(0.0005)
 
def lcd_byte(bits, mode):
  GPIO.output(pantalla_RS, mode) 

  GPIO.output(pantalla_D4, False)
  GPIO.output(pantalla_D5, False)
  GPIO.output(pantalla_D6, False)
  GPIO.output(pantalla_D7, False)
  if bits&0x10==0x10:
    GPIO.output(pantalla_D4, True)
  if bits&0x20==0x20:
    GPIO.output(pantalla_D5, True)
  if bits&0x40==0x40:
    GPIO.output(pantalla_D6, True)
  if bits&0x80==0x80:
    GPIO.output(pantalla_D7, True)
 
  lcd_toggle_enable()
 
  GPIO.output(pantalla_D4, False)
  GPIO.output(pantalla_D5, False)
  GPIO.output(pantalla_D6, False)
  GPIO.output(pantalla_D7, False)
  if bits&0x01==0x01:
    GPIO.output(pantalla_D4, True)
  if bits&0x02==0x02:
    GPIO.output(pantalla_D5, True)
  if bits&0x04==0x04:
    GPIO.output(pantalla_D6, True)
  if bits&0x08==0x08:
    GPIO.output(pantalla_D7, True)
 
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  sleep(0.0005)
  GPIO.output(pantalla_E, True)
  sleep(0.0005)
  GPIO.output(pantalla_E, False)
  sleep(0.0005)
 
def lcd_string(message,line):
 
  message = message.ljust(32," ")
 
  lcd_byte(line, False)
 
  for i in range(32):
    lcd_byte(ord(message[i]),True)
 
 

#Función para ingresar creditos a la tarjeta
def ingresoCreditos(id,creditoAg):
 stringLectur = "/ID/"+id+"/Monedero/Credito"
 creditoActual = firebase.get(stringLectur,"")
 creditoNuevo = creditoActual+creditoAg
 stringPut = "/ID/"+id+"/Monedero"
 firebase.put(stringPut, "/Credito",creditoNuevo)
 
 #Loop de la raspberry para el funcionamiento del proyecto
def peripheral_loop():
 encendidoRFID = False
 matriculas = firebase.get("/ID","")
 if GPIO.input(btInicio):
  encendidoRFID = True
 while encendidoRFID:
  #prints("Deslice la tarjeta\r ")
  lcd_string("Deslice la Tarjeta", 0x80)
  mensaje = recibir()
  if mensaje in matriculas:
   lecturaNombre = matriculas[mensaje]["Nombre"]
   saldoActual = matriculas[mensaje]["Monedero"]["Credito"]
   printsln("Bienvenido " + lecturaNombre+"\r")
   lcd_string("Bienvenido "+ lecturaNombre, 0x80)
   lcd_string("Saldo:  "+ str(saldoActual), 0xC0)
   while 1:
    if GPIO.input(btFin):
     encendidoRFID = False
     lcd_string("Gracias #Espol!!", 0x80)
     lcd_string("", 0xC0)
     sleep(2)
     lcd_string("Bienvenido!!", 0x80)
     break
    if GPIO.input(bt1):
     while GPIO.input(bt1):
      GPIO.output(ld1, GPIO.HIGH)
     GPIO.output(ld1, GPIO.LOW)
     ingresoCreditos(mensaje,100)
     #printsln("Se Actualizo el saldo\r")
     lcd_string("100 Creditos Agregados!", 0xC0)
     sleep(2)
    elif GPIO.input(bt2):
     while GPIO.input(bt2):
      GPIO.output(ld2, GPIO.HIGH)
     GPIO.output(ld2, GPIO.LOW)
     ingresoCreditos(mensaje, 25)
     lcd_string("25 Creditos Agregados!", 0xC0)
     sleep(2)
    lcd_string("Saldo:  "+ str(firebase.get("/ID/"+mensaje+"/Monedero/Credito" ,"")), 0xC0)
  else:
   #printsln("Matricula no valida ingrese una correctamente\r")
   lcd_string("Tarjeta no valida", 0x80)
   sleep(2)
   lcd_string("Bienvenido", 0x80)
   break
  
   
 

def main () :

# Setup
 peripheral_setup()

# Infinite loop
 try:
  while True :  
   peripheral_loop()
   pass
 except(KeyboardInterrupt,SystemExit):
  print ("BYE")
  GPIO.cleanup()
# Command line execution
if __name__ == '__main__' :
   main()