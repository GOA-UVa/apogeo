# Apogeo

Software encargado de recibir los datos del DataLogger CR300 que recibe datos de los apogees situados en la Base Marambio, y enviar esos mismos datos a un servidor sftp del GOA.

Archivos presentes:
- cr300: Modulo de python que permite acceder a los datos del CR300.
- read_data.py: Script principal en python que lee el CR300 y sube los datos al servidor sftp.
- apo2.CR300: Programa que se ejecuta dentro del CR300.
- requirements.txt: Requisitos del entorno de python para poder ejecutar el read_data.py
- run.bat: Fichero .bat para poder ejecutar el programa en cada arranque de Windows.
- config.mock.json: Fichero json con datos de ejemplo que deberán ser sustituidos con los reales en producción, y guardado como config.json.

## Como instalar y ejecutar

### Código del CR300

Para instalar/actualizar el código del DataLogger el usuario deberá
abrir el programa PC400 y establecer una conexión con el CR300. Ahí se
le presentará la opción "Send Program...", la cual pulsará. A partir
de ahí el usuario ha de seleccionar el programa apo2.CR300 que se
enviará al DataLogger. Es importante cambiar el formato de ficheros a
mostrar de 'Program Files (\*.crb)' a 'All files (*)'.

### Código de python

#### Entorno virtual

La siguiente información está explicada para ejecutar en Windows, en
Linux es levemente distinto pero se asume que el usuario de Linux sabe
encontrar los cambios necesarios.

Idealmente este código se ejecutará en un entorno de ejecución de venv,
que debería llamarse '.venv'. Si este directorio no existe, debería ser creado con:
```sh
python -m venv .venv
```

A continuación se activa el entorno de ejecución con:
```sh
.venv\Scripts\activate
```

Y finalmente se prepara el entorno virtual instalando los paquetes necesarios con:
```sh
pip install -r requirements.txt
```

#### Ejecución

La ejecución simplemente deberá ser realizada mediante el fichero run.bat, que deberá
indicarse a windows que se quiere ejecutar en cada arranque del equipo para que siempre se ejecute.

## Como encontrar el puerto

El nombre del puerto al que está conectado el CR300 deberá introducirse en el campo "serialport"
del fichero config.json.

En Windows habitualmente es "COM4" y en Linux "/dev/ttyACM0". En Linux también puede introducirse
el id directamente, lo cual quedaría para la instalación actual como:
"/dev/serial/by-id/usb-Campbell_Scientific__Inc._CR300_00000000050C-if00".

### Linux

sudo dmesg | grep tty

### Windows

Via el explorador de dispositivos.

## Serial CMD help output

```
Status Commands
  show timeout list (PakBus timeout list)
  show time queue (Time Queue (RTOS))
  show time (Display Time)
  show status (Status)
  show errors (Errors)
  show settings fields (Settings Fields)
  show settings (Settings)
  show scan (Scan Information)
  show vars (Public Variables)
  show records (Start / Continue Record Output)
  show table structure (Table structure (CRBASIC Format))
  show table (Data Table Info)
  show inlocs (Read Inloc Binary)
  show device info (Device Information)
  show tasks (Task / Debug Info)
  show task memory (Task Memory)
  show watchdog counters (Watchdog Counters)
  show watchdog timers (Watchdog timers)
  show watchdog (Watchdog File)
  show wnvars (Public Variables w/o names)
  show trace detail xx_hex_xx (Mem Trace Detail)
  show mem trace (Memory Trace List)
  show memory (Memory)
  show os history (OS Update History)
  show program line number (Program execution line numbers)
  show program (CR-Basic Program)
  show calibration (Calibration Table)
  show temperature (Temperature (Internal))
  show battery (Battery Voltage)
  show dnp stats (DNP3 stats)
  show routers neighbors (Routers and neighbors)
  show routes (Routes)
  show link states (PakBus link states)
  show expect more (PakBus expect more list)
  show tcp listen (TCP Listen list)
  show tcp sockets (TCP socket list)
  show pakbus clients (PakBus/TCP Clients)
  show file system (File System Information)
  show IP INFO #net (IP Info)
  show IP mem (IP memory detail)
  show IP Route (IP Route list)
  show events (Events (RTOS))
  show web status (Web update status)
  show cellular Info (Cellular info)
  show cellular errors (Cellular error summary)
  show cellular log (Cellular error log)
  show cellular update status (Cellular firmware update status
  show modbus stats (Modbus stats)
  show preserve (PreserveVariables Info)
  show GOES (GOES state)
  show SMS TX (SMS Tx Log)
  show SMS RX (SMS Rx Queue)
Set Commands
  set comms watch (Comms Watch)
  set const table (Edit const table)
  set term mast (Terminal Master)
  set cellular pdp clear (sets flag to clear stored PDP conten
  set cellular MBN reset (sets flag to reset cellular MBN)
Action Commands
  reboot (Restart, compile and run program)
  clear watchdog (Clear watchdog counts)
  clear SFE (Clear SF errors)
  stop comms watch (stop comms watch)
  SDI12 (SDI-12 talk through)
  talk through (Serial Talk Through)
  web update (Web files update start)
  cellular update (Cellular update)
  cellular radio update (Cellular radio update)
  cellular reset (Cellular reset)
  PCAP capture (Wireshark PCAP capture)
```
