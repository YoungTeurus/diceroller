import socket
import json

rolled_numbers = []  # Выпавшие числа
roll_sum = 0  # Сумма выпавших чисел
num_of_rolled_dices = 0  # Количество брошенных кубиков
roll_dimention = 0  # Количество граней у каждого кубика
roll_bonus = 0  # Бонус для прибавления к кубикам

data_dict = {
    "rolled_numbers": rolled_numbers,
    "roll_sum": roll_sum,
    "num_of_rolled_dices": num_of_rolled_dices,
    "roll_dimention": roll_dimention,
    "roll_bonus": roll_bonus
}

if __name__ == "__main__":
    print(data_dict)

    sock = socket.socket()
    sock.connect(('localhost', 19090))

    data = sock.recv(1024).decode()
    data_dict = json.loads(data)
    sock.close()

    print(data_dict)