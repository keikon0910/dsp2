import math
import flet as ft


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE


class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.LIGHT_BLUE_100
        self.color = ft.colors.BLACK


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        ActionButton(text="AC", button_clicked=self.button_clicked),
                        ActionButton(text="+/-", button_clicked=self.button_clicked),
                        ScientificButton(text="√", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(
                            text="0", expand=2, button_clicked=self.button_clicked
                        ),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Text("Scientific Functions", color=ft.colors.LIGHT_BLUE, size=18),
                ft.Row(
                    controls=[
                        ScientificButton(text="sin", button_clicked=self.button_clicked),
                        ScientificButton(text="cos", button_clicked=self.button_clicked),
                        ScientificButton(text="tan", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ScientificButton(text="log", button_clicked=self.button_clicked),
                        ScientificButton(text="ln", button_clicked=self.button_clicked),
                        ScientificButton(text="e^x", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ScientificButton(text="x^y", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        try:
            if data == "AC":
                self.result.value = "0"
                self.reset()

            elif data == "=":
                if "^" in self.result.value:
                    base, exponent = map(float, self.result.value.split("^"))
                    self.result.value = str(math.pow(base, exponent))
                else:
                    self.result.value = str(eval(self.result.value))
                self.reset()

            elif data == "√":
                self.result.value = str(math.sqrt(float(self.result.value)))

            elif data == "sin":
                self.result.value = str(math.sin(math.radians(float(self.result.value))))

            elif data == "cos":
                self.result.value = str(math.cos(math.radians(float(self.result.value))))

            elif data == "tan":
                self.result.value = str(math.tan(math.radians(float(self.result.value))))

            elif data == "log":
                self.result.value = str(math.log10(float(self.result.value)))

            elif data == "ln":
                self.result.value = str(math.log(float(self.result.value)))

            elif data == "e^x":
                self.result.value = str(math.exp(float(self.result.value)))

            elif data == "x^y":
                self.result.value += "^"

            elif data == "+/-":
                self.result.value = str(-float(self.result.value))

            else:
                if self.result.value == "0":
                    self.result.value = data
                else:
                    self.result.value += data

        except Exception as ex:
            self.result.value = "Error"
            print(f"Error: {ex}")

        self.update()

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Scientific Calculator"
    calc = CalculatorApp()
    page.add(calc)


ft.app(target=main)