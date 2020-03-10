import sys  # sys нужен для передачи argv в QApplication
import diceroller_v1_1
import random
from PyQt5 import QtWidgets
import time
import socketserver
import socket
import json
import threading

texts = (
    "Вы бросили: ",  # 0
    "Выпали числа: ",  # 1
    "Общая сумма: ",  # 2
    "с учётом бонуса",  # 3
    "Сервер запущен! Ожидание подключения.\n"  # 4
)

errors_texts = (
    "Ошибок нет!",  # 0
    "Проверьте значения полей ввода!",  # 1
    "Количество кубиков не может быть отрицательным числом!",  # 2
    "Количество граней кубика не может быть отрицательным числом!"  # 3
)


class MyUDPHandler(socketserver.BaseRequestHandler):
    DiceRoller_object = None

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request[0].decode()  # Вытаскиваем data
        data_dict = json.loads(data)  # Делаем из этого словарь
        print("{} wrote: ".format(self.client_address[0]), end="")
        print(data_dict)
        self.DiceRoller_object.parse_data(data_dict)
        self.DiceRoller_object.show_roll_result()
        self.DiceRoller_object.ip = self.client_address[0]
        self.DiceRoller_object.ip_line.setText(self.DiceRoller_object.ip)
        # print(data)
        # just send back the same data, but upper-cased
        # self.request.sendall(self.data.upper())


class DiceRoller(QtWidgets.QMainWindow, diceroller_v1_1.Ui_MainWindow):
    rolled_numbers = []  # Выпавшие числа
    roll_sum = 0  # Сумма выпавших чисел
    num_of_rolled_dices = 1  # Количество брошенных кубиков
    roll_dimention = 20  # Количество граней у каждого кубика
    roll_bonus = 0  # Бонус для прибавления к кубикам
    roll_from = "local"

    # server_thread = None  # Поток для поддержания сервера
    server = None  # Сервер
    ip = "localhost"

    def __init__(self):
        super().__init__()
        # Дизайн модели и связывание событий
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.rollDice_button.clicked.connect(self.roll_dice)
        self.createServer_button.clicked.connect(self.create_server)
        # self.connect_button.setEnabled(False)  # Отключаем кнопку подключиться к серверу
        self.connect_button.clicked.connect(self.connect_to_server)

        # Установка начальных значений
        self.set_dice_variables()

    def closeEvent(self, *args, **kwargs):
        """
        Перехват события завершения работы приложения
        """
        if self.server is not None:
            self.server.shutdown()

    def roll_dice(self):
        """
        Выбрасывает указанное количество кубиков
        """
        self.rolled_numbers.clear()  # Сброс выпавших чисел
        self.roll_sum = 0
        self.roll_from = "local"

        # Получение значений из полей для ввода
        if (error := self.get_dice_variables()) != 0:  # Если произошла ошибка
            self.show_text(errors_texts[error], True)  # Показать её текст
            return  # Не бросать кубики

        for dice in range(self.num_of_rolled_dices):
            rolled_number = random.randint(1, self.roll_dimention)
            self.rolled_numbers.append(rolled_number)
            self.roll_sum += rolled_number
        self.roll_sum += self.roll_bonus

        self.show_roll_result()

    def get_dice_variables(self):
        '''
        Устанавливает значения для броска из полей для ввода
        '''

        # Получение введённых значений

        # Количество кубиков
        try:
            self.num_of_rolled_dices = int(self.diceCount_line.text())
        except ValueError:
            if self.diceCount_line.text().__len__() != 0:
                return 1  # Возникла ошибка №1 - "Проверьте значения полей ввода!"
            # Если поле ввода числа кубиков пустое, считаем, что кинули 1 кубик
            self.diceCount_line.setText("1")
            self.num_of_rolled_dices = 1

        # Количество граней кубика
        try:
            self.roll_dimention = int(self.diceDimentional_line.text())
        except ValueError:
            if self.diceDimentional_line.text().__len__() != 0:
                return 1  # Возникла ошибка №1 - "Проверьте значения полей ввода!"
            # Если поле ввода числа граней кубиков пустое, считаем, что кинули d20 кубик
            self.diceDimentional_line.setText("20")
            self.roll_dimention = 20

        # Сумма бонуса
        try:
            self.roll_bonus = int(self.diceBonus_line.text())
        except ValueError:
            if self.diceBonus_line.text().__len__() != 0:
                return 1  # Возникла ошибка №1 - "Проверьте значения полей ввода!"
            # Если поле ввода бонуса броска пустое, считаем, что бонус равен 0
            self.roll_bonus = 0
            self.diceBonus_line.setText("0")

        # Проверка введённых значений на легальность

        if self.num_of_rolled_dices < 0:
            return 2  # Возникла ошибка №2 - "Количество кубиков не может быть отрицательным числом!"
        if self.num_of_rolled_dices > 100:
            self.num_of_rolled_dices = 100
            self.diceCount_line.setText("100")

        if self.roll_dimention < 0:
            return 3  # Возникла ошибка №3 - "Количество граней кубика не может быть отрицательным числом!"
        if self.roll_dimention > 1000000:
            self.roll_dimention = 1000000
            self.diceDimentional_line.setText("1000000")

        return 0  # Нет ошибки

    def set_dice_variables(self):
        '''
        Устанавливает значение полей ввода в соответствии с сохранёнными данными
        '''
        self.diceDimentional_line.setText(str(self.roll_dimention))
        self.diceCount_line.setText(str(self.num_of_rolled_dices))
        self.diceBonus_line.setText(str(self.roll_bonus))

    def show_roll_result(self):
        '''
        Отображает результат сохранённого броска кубиков в result_text
        '''
        text_to_set = ""  # Текст для отображения в result_text

        # Вывод времени броска
        text_to_set += "[{}] ".format(
            time.strftime("%H:%M:%S", time.gmtime(time.time()))
        )

        text_to_set += "от <{}>\n".format(
            self.roll_from
        )

        text_to_set += texts[0]  # "Вы бросили: "
        symbol_before_bonus = "+"  # Отображаемый символ перед бонусом броска
        if self.roll_bonus < 0:
            symbol_before_bonus = ""
        text_to_set += "{0}d{1}{3}{2}\n".format(self.num_of_rolled_dices,
                                                self.roll_dimention,
                                                self.roll_bonus,
                                                symbol_before_bonus)
        text_to_set += "\n"

        text_to_set += texts[1]  # "Выпали числа: "
        for dice in range(self.num_of_rolled_dices):
            text_to_set += str(self.rolled_numbers[dice])  # Вывод самих чисел
            if dice < self.num_of_rolled_dices - 1:
                text_to_set += ", "  # Вывод запятой, кроме последнего кубика

        text_to_set += "\n"
        text_to_set += texts[2]  # "Общая сумма: "
        text_to_set += str(self.roll_sum - self.roll_bonus)
        if self.roll_bonus != 0:
            text_to_set += " ({0} {1} {2})".format(str(self.roll_sum),
                                                   texts[3],  # "с учётом бонуса"
                                                   str(self.roll_bonus))
        text_to_set += "\n"
        text_to_set += "\n"

        self.show_text(text_to_set, True)  # Вывод текста

    def show_text(self, text, add=False):
        '''
        Отображает text в result_text
        '''
        # if add is True:
        #   last_text = self.result_text.toPlainText()
        #    text += last_text
        # self.result_text.setText(text)
        if add is False:
            self.result_text.clear()
        self.result_text.append(text)

    def create_server(self):
        # Пока что работаем с localhost
        # self.ip = self.ip_line.text()
        class MyUDPHandler_with_object(MyUDPHandler):  # Костыль(?)
            DiceRoller_object = self  # Передаю ссылку на объект

        HOST, PORT = "localhost", 9999
        self.server = socketserver.UDPServer((HOST, PORT), MyUDPHandler_with_object)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()

        self.show_text(texts[4], True)

    def connect_to_server(self):
        self.ip = self.ip_line.text()

        # Пока что просто пытаемся отправить data
        HOST, PORT = self.ip, 9999
        data_dict = {
            "rolled_numbers": self.rolled_numbers,
            "roll_sum": self.roll_sum,
            "num_of_rolled_dices": self.num_of_rolled_dices,
            "roll_dimention": self.roll_dimention,
            "roll_bonus": self.roll_bonus,
            "roll_from" : "remote"
        }
        data = json.dumps(data_dict)
        # SOCK_DGRAM is the socket type to use for UDP sockets
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # As you can see, there is no connect() call; UDP has no connections.
        # Instead, data is directly sent to the recipient via sendto().
        sock.sendto(data.encode(), (HOST, PORT))
        print("Sent to {}:{} : {}".format(HOST,PORT,data))

    def parse_data(self, data):
        """
        Присваивает локальным значениям переменных значения из словаря data.
        """
        self.rolled_numbers = data['rolled_numbers']
        self.roll_sum = data['roll_sum']
        self.num_of_rolled_dices = data['num_of_rolled_dices']
        self.roll_dimention = data['roll_dimention']
        self.roll_bonus = data['roll_bonus']
        self.roll_from = data['roll_from']


if __name__ == "__main__":
    random.seed()
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = DiceRoller()  # Создаём объект класса DiceRoller
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
