# 에러 발생시 호출 되는 에러클래스

class EmptyError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "필수 입력을 확인 하세요.({})".format(self.value)


class WrongValueError(Exception):

    def __init__(self, in_value, correct_value):
        self.in_value = in_value
        self.correct_value = correct_value

    def __str__(self):
        return "입력값을 확인 하세요. 입력값: {}, 올바른 값: {}".format(self.in_value, self.correct_value)


