class ValueWrapper:
    def __init__(self, value: any, callback_event: callable):
        self.value: any = value
        self.callback_event: callable = callback_event

    def get(self):
        return self.value

    def set(self, new_value: any):
        self.value = new_value
        self.callback_event()


def event_handler():
    print("the value has changed")


value = ValueWrapper("carlos", callback_event=event_handler)
value.set("henrique")
