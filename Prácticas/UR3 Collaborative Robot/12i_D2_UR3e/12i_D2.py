import socket
import time
import math

# Función para enviar una trayectoria en espacio de configuraciones a la controladora del robot
def send_joint_path(path, sock):
    for joint_config in path:
        print(joint_config)
        sock.send(f"movej({joint_config}, a=0.5, v=0.5)".encode() + "\n".encode())
        time.sleep(1)

def send_linear_path(path, sock):
    for linear_config in path:
        print(linear_config)
        sock.send(f"movel(p{linear_config}, a=0.5, v=0.5)".encode() + "\n".encode())
        time.sleep(1)

def send_joint_position(position, sock):
    sock.sendall(f"movej({position}, a=0.2, v=0.3)".encode() + "\n".encode())
    time.sleep(2)

def send_linear_position(pose, sock):
    sock.sendall(f"movel(p{pose}, a=0.2, v=0.3)".encode() + "\n".encode())
    time.sleep(2)

def send_script_file(filename, sock):
    with open(filename, "rb") as f:
        program = f.read()
    sock.sendall(program + "\n".encode())
    time.sleep(2)

def open_grip(sock):
    send_script_file(Abrir_pinza, sock)

def close_grip(sock):
    send_script_file(Cerrar_pinza, sock)

def offset_position_pick(pick_init, i):
    return [
                pick_init[0],
                pick_init[1],
                pick_init[2] - (piece_height * i),
                pick_init[3],
                pick_init[4],
                pick_init[5],
            ]

def offset_position_drop(drop_init, i):
    return [
                drop_init[0] + ((piece_width + drop_dist) * i),
                drop_init[1],
                drop_init[2],
                drop_init[3],
                drop_init[4],
                drop_init[5],
            ]

# Dirección IP del robot UR
HOST = "10.10.73.239" # UR05 = 8, UR06 = 9

# Puerto del servidor en el robot
PORT = 30002

# Scripts para abrir y cerrar la pinza
Abrir_pinza = 'pinza40UR3.py'
Cerrar_pinza = 'pinza10UR3.py'

# Type of movement
JOINT = 0
LINEAR = 1

# Offset values
num_pieces = 4
piece_height = 0.02
piece_width = 0.03
drop_dist = 0.01

# Joint (angles)
pick_home_joint = [29.13, -68.08, 53.56, -76.25, -86.85, 40]
drop_home_joint = [44.75, -64.65, 45.83, -72.71, -87.15, 40]
# linear (angles)
pick_home_linear = [-266.11, -317.26, 111.75, 2.126, 2.3, 0]
drop_home_linear = [-181.20, -385.20,  122.30, 2.126, 2.3, 0]
pick_0 = [-266.11, -317.26, 59.16, 2.126, 2.3, 0]
drop_0 = [-228.80, -428.17, 5.1, 2.126, 2.3, 0]

# Angles to radians
pick_home_joint = [math.radians(x) for x in pick_home_joint]
drop_home_joint = [math.radians(x) for x in drop_home_joint]
for i in range(0,3):
    pick_home_linear[i] = pick_home_linear[i]/1000
    drop_home_linear[i] = drop_home_linear[i]/1000
    pick_0[i] = pick_0[i]/1000
    drop_0[i] = drop_0[i]/1000

# Conexión via socket a la controladora del robot
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
time.sleep(1)

# Sequence
# -> Home Pick (J) -> Piece i (L) -> Close grip -> Home Pick (L) -> 
# -> Home Drop (J) -> Piece i (L) -> Open grip -> Home Drop (L) -> 

# Init
open_grip(sock)
time.sleep(1)

# Pieces
for i in range(num_pieces):
    # Pick
    print(f"Pick Home (JOINT): {pick_home_joint}")
    send_joint_position(pick_home_joint, sock)

    pick_i = offset_position_pick(pick_0, i)
    print(f"Pick piece {i} (LINEAR): {pick_i}")
    send_linear_position(pick_i, sock)

    print(f"Close Grip")
    close_grip(sock)

    print(f"Pick Home (LINEAR): {pick_home_linear}")
    send_linear_position(pick_home_linear, sock)

    # Drop
    print(f"Drop Home (JOINT): {drop_home_joint}")
    send_joint_position(drop_home_joint, sock)

    drop_i = offset_position_drop(drop_0, i)
    print(f"Drop piece {i} (LINEAR): {drop_i}")
    send_linear_position(drop_i, sock)

    print(f"Open Grip")
    open_grip(sock)

    print(f"Drop Home (LINEAR): {drop_home_linear}")
    send_linear_position(drop_home_linear, sock)

# Mensaje que se imprime cuando se finaliza la ejecución
# de la trayectoria
print("Trayectoria finalizada")

data = sock.recv(1024)

# Se cierra la conexión
sock.close()


"""
ROB/D2> python3 UR3_12i.py
Pick Home (JOINT): [0.5084144111059482, -1.1882201547577396, 0.9347983473681629, -1.3308135546456763, -1.515818455357075, 0.6981317007977318]
Pick piece 0 (LINEAR): [-0.26611, -0.31726, 0.05916, 2.126, 2.3, 0]
Close Grip
Pick Home (LINEAR): [-0.26611, -0.31726, 0.11175, 2.126, 2.3, 0]
Drop Home (JOINT): [0.7810348402674625, -1.1283553614143342, 0.7998843961890012, -1.2690288991250769, -1.5210544431130584, 0.6981317007977318]
Drop piece 0 (LINEAR): [-0.2288, -0.42817, 0.0050999999999999995, 2.126, 2.3, 0]
Open Grip
Drop Home (LINEAR): [-0.1812, -0.3852, 0.12229999999999999, 2.126, 2.3, 0]
Pick Home (JOINT): [0.5084144111059482, -1.1882201547577396, 0.9347983473681629, -1.3308135546456763, -1.515818455357075, 0.6981317007977318]
Pick piece 1 (LINEAR): [-0.26611, -0.31726, 0.03916, 2.126, 2.3, 0]
Close Grip
Pick Home (LINEAR): [-0.26611, -0.31726, 0.11175, 2.126, 2.3, 0]
Drop Home (JOINT): [0.7810348402674625, -1.1283553614143342, 0.7998843961890012, -1.2690288991250769, -1.5210544431130584, 0.6981317007977318]
Drop piece 1 (LINEAR): [-0.1888, -0.42817, 0.0050999999999999995, 2.126, 2.3, 0]
Open Grip
Drop Home (LINEAR): [-0.1812, -0.3852, 0.12229999999999999, 2.126, 2.3, 0]
Pick Home (JOINT): [0.5084144111059482, -1.1882201547577396, 0.9347983473681629, -1.3308135546456763, -1.515818455357075, 0.6981317007977318]
Pick piece 2 (LINEAR): [-0.26611, -0.31726, 0.019159999999999996, 2.126, 2.3, 0]
Close Grip
Pick Home (LINEAR): [-0.26611, -0.31726, 0.11175, 2.126, 2.3, 0]
Drop Home (JOINT): [0.7810348402674625, -1.1283553614143342, 0.7998843961890012, -1.2690288991250769, -1.5210544431130584, 0.6981317007977318]
Drop piece 2 (LINEAR): [-0.1488, -0.42817, 0.0050999999999999995, 2.126, 2.3, 0]
Open Grip
Drop Home (LINEAR): [-0.1812, -0.3852, 0.12229999999999999, 2.126, 2.3, 0]
Pick Home (JOINT): [0.5084144111059482, -1.1882201547577396, 0.9347983473681629, -1.3308135546456763, -1.515818455357075, 0.6981317007977318]
Pick piece 3 (LINEAR): [-0.26611, -0.31726, -0.0008400000000000005, 2.126, 2.3, 0]
Close Grip
Pick Home (LINEAR): [-0.26611, -0.31726, 0.11175, 2.126, 2.3, 0]
Drop Home (JOINT): [0.7810348402674625, -1.1283553614143342, 0.7998843961890012, -1.2690288991250769, -1.5210544431130584, 0.6981317007977318]
Drop piece 3 (LINEAR): [-0.10880000000000001, -0.42817, 0.0050999999999999995, 2.126, 2.3, 0]
Open Grip
Drop Home (LINEAR): [-0.1812, -0.3852, 0.12229999999999999, 2.126, 2.3, 0]
Trayectoria finalizada
"""
