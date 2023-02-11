# Практическое задание: игра "Морской бой"
import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    """Класс описывающий точку на игровом поле"""
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __eq__(self, other_dot):
        return self.x == other_dot.x and self.y == other_dot.y


class Ship:
    """Класс описывающий корабли на игровом поле
    :param
        length: длина корабля в клетках
        nose: точка размещения носа корабля
        orientation: 0 - вертикальное расположение, 1 - горизонтальное
            направление считается слева на право и сверху вниз соответственно, от коодинат точки носа корабля
        lifes: кол-во оставшихся жизней корабля
    """
    def __init__(self, nose, length, orientation):
        self.nose = nose
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        """Метод возвращает все точки корабля"""
        for i in range(self.length):
            if self.orientation == 0:
                return [Dot(self.nose.x + i, self.nose.y) for i in range(self.length)]
            elif self.orientation == 1:
                return [Dot(self.nose.x, self.nose.y + i) for i in range(self.length)]

    def shooten(self, shot):
        """Метод проверяет попадаение в корабль"""
        return shot in self.dots


class Board:
    """Класс описывающий доску"""
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        """Вывод поля"""
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, dot):
        """Проверка попадание точки в границы доски"""
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, verb=False):
        """Отрисовка контура вокруг корабля"""
        nearby_dots = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in nearby_dots:
                current = Dot(dot.x + dx, dot.y + dy)
                if not (self.out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = "."
                    self.busy.append(current)

    def add_ship(self, ship):
        """Метод добавления корабля"""
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        """Метод описывающий выстрел"""
        if self.out(dot):
            raise BoardOutException()
        if dot in self.busy:
            raise BoardUsedException()
        self.busy.append(dot)
        for ship in self.ships:
            if ship.shooten(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    """Класс игрок"""
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        """Метод запроса выстрела"""
        raise NotImplementedError()

    def move(self):
        """Метод описывающий ход"""
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as exception:
                print(exception)


class AI(Player):
    """Класс Игрок - ПК"""
    def ask(self):
        dot = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
        return dot


class User(Player):
    """Класс Игрок - пользователь"""
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    """Класс - игровой процесс"""
    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        pc_board = self.random_board()
        pc_board.hid = True
        self.ai = AI(pc_board, player_board)
        self.us = User(player_board, pc_board)

    def greet(self):
        """метод, который приветствует пользователя"""
        print('Игра "Морской бой')
        print('Формат ввода: номер строки, пробел, номер столбца.')
        print('Пример: 1 1')

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(random.randint(0, self.size), random.randint(0, self.size)), l, random.randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        """метод генерирует случайную доску"""
        board = None
        while board is None:
            board = self.try_board()
        return board

    def loop(self):
        """метод с игровым циклом"""
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        """запуск игры"""
        self.greet()
        self.loop()


my_game = Game()
my_game.start()
