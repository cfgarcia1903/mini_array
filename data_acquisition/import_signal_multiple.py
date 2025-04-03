import serial
import time
import glob
import sys
import signal
import threading
from params import *  # Import parameters from params.py

def signal_handler(signal, frame):
    print("\nClosing all ports and files...")
    for ComPort in ports:
        ComPort.close()
    for f in files:
        f.close()
    sys.exit(0)

def serial_ports():
    """ Lists available serial ports """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError("Unsupported platform")
    
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def read_device(port_index, filename):
    """ Reads data from a specific serial port and writes to a file """
    ComPort = serial.Serial(port_list[port_index], baudrate=9600, bytesize=8, parity='N', stopbits=1)
    ports.append(ComPort)

    file = open(filename, "w", buffering=1)
    files.append(file)

    print(f"Recording data from {port_list[port_index]} to {filename}...")

    counter = 0
    while True:
        data = ComPort.readline().decode('utf-8')  # Read and decode data
        if counter == 0:
            file.write("###################################################################################\n")
            file.write(f"### CosmicWatch: The Desktop Muon Detector\n### Device ID: {port_list[port_index]}\n")
            file.write("### Comp_date Comp_time Event Ardn_time[ms] ADC_value[0-1023] SiPM[mV] Deadtime[ms]\n")
            file.write("###################################################################################\n")
        file.write(data)
        counter += 1

# ────────────────────────────────────────────────────────────────────
#                  1️⃣ DETECTAR PUERTOS DISPONIBLES
# ────────────────────────────────────────────────────────────────────
port_list = serial_ports()
if len(port_list) < 2:
    print("At least two serial devices are required. Exiting...")
    sys.exit(1)

print("\nAvailable serial ports:")
for i, port in enumerate(port_list):
    print(f"[{i+1}] {port}")

# ────────────────────────────────────────────────────────────────────
#                  2️⃣ SELECCIONAR PUERTOS
# ────────────────────────────────────────────────────────────────────
port1 = int(input("Select first Arduino port: ")) - 1
port2 = int(input("Select second Arduino port: ")) - 1

#file1 = input("Enter filename for first device: ")
#file2 = input("Enter filename for second device: ")

# ────────────────────────────────────────────────────────────────────
#                  3️⃣ CONFIGURAR SEÑAL PARA Ctrl+C
# ────────────────────────────────────────────────────────────────────
signal.signal(signal.SIGINT, signal_handler)

# ────────────────────────────────────────────────────────────────────
#                  4️⃣ INICIAR HILOS PARA CADA DISPOSITIVO
# ────────────────────────────────────────────────────────────────────
ports = []
files = []

thread1 = threading.Thread(target=read_device, args=(port1, file1))
thread2 = threading.Thread(target=read_device, args=(port2, file2))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
