class Agent:
    def __init__(self, mode:str='shell'):
        super().__init__()
        self.mode = mode
    
    def get_answer(self):
        get_answer_mapping = {
            'shell': self.get_answer_shell
        }
        worker_function = get_answer_mapping[self.mode]
        return worker_function()
    
    def get_answer_shell(self):
        res = input()
        return res
    
    def ask(self, question:str=''):
        print(question)
        answer = self.get_answer()
        return answer