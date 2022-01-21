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

#Variables Motor
servo = 25

#Variables para el selector de monedas
bt1 = 22
bt2 = 27

#Definición de pines para el LCD
pantalla_RS = 5
pantalla_E  = 6
pantalla_D4 = 12
pantalla_D5 = 13
pantalla_D6 = 16
pantalla_D7 = 19

#Recibe la información Guardada en la tarjeta
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
 GPIO.setwarnings(False)
 GPIO.setmode(GPIO.BCM)
 GPIO.setup(bt1, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(bt2, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(btInicio, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(btFin, GPIO.IN, GPIO.PUD_DOWN)
 GPIO.setup(servo, GPIO.OUT)
 GPIO.setup(pantalla_RS, GPIO.OUT)  
 GPIO.setup(pantalla_E, GPIO.OUT) 
 GPIO.setup(pantalla_D4, GPIO.OUT) 
 GPIO.setup(pantalla_D5, GPIO.OUT) 
 GPIO.setup(pantalla_D6, GPIO.OUT) 
 GPIO.setup(pantalla_D7, GPIO.OUT) 
 
 lcd_init()
 
 
 lcd_string("Bienvenido!!", 0x80)
 #lcd_string("TechToob",0xC0)


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

  
#Función para comprar la comida
def compraComida(id, menu,tipo):
 stringLectur = "/ID/"+id+"/Monedero/Credito"
 stringDescuento = "/ID/"+id+"/Descuento"
 creditoActual = firebase.get(stringLectur,"")
 descuento = float(firebase.get(stringDescuento, ""))
 valor = int(menu*descuento)
 if creditoActual < valor:
  lcd_string("Saldo insuficiente!", 0xC0)
 else:
  creditoActual -= menu*descuento
  lcd_string("Compra Exitosa del  menu "+str(tipo)+"!!", 0xC0)
  GPIO.output(servo, GPIO.HIGH)
  sleep(5)
  GPIO.output(servo, GPIO.LOW)
 creditoNuevo = creditoActual
 stringPut = "/ID/"+id+"/Monedero"
 firebase.put(stringPut, "/Credito",creditoNuevo)
 
 
#Loop de la raspberry para el funcionamiento del proyecto
def peripheral_loop():
 encendidoRFID = False
 matriculas = firebase.get("/ID","")
 if GPIO.input(btInicio):
  encendidoRFID = True
 while encendidoRFID:
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
     sleep(1)
     lcd_string("Bienvenido!!", 0x80)
     break
    if GPIO.input(bt1):
     compraComida(mensaje, 250,1)
    elif GPIO.input(bt2):
     compraComida(mensaje, 350,2)
    lcd_string("Saldo:  "+ str(firebase.get("/ID/"+mensaje+"/Monedero/Credito" ,"")), 0xC0)
  else:
   lcd_string("Tarjeta no valida", 0x80)
   sleep(1)
   lcd_string("Bienvenido", 0x80)
   break
 #printsln("Proceso Finalizado")
  
   
 

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