import socket
import json

rolled_numbers = [3,2]  # Выпавшие числа
roll_sum = 3  # Сумма выпавших чисел
num_of_rolled_dices = 5  # Количество брошенных кубиков
roll_dimention = -6  # Количество граней у каждого кубика
roll_bonus = 41241  # Бонус для прибавления к кубикам

data_dict = {
    "rolled_numbers": rolled_numbers,
    "roll_sum": roll_sum,
    "num_of_rolled_dices": num_of_rolled_dices,
    "roll_dimention": roll_dimention,
    "roll_bonus": roll_bonus
}

if __name__ == "__main__":
    sock = socket.socket()
    sock.bind(('', 19090))
    sock.listen(1)
    conn, addr = sock.accept()

    print('connected:', addr)

    data = json.dumps(data_dict)

    conn.send(data.encode())

    conn.close()
