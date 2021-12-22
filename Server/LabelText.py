from tkinter import *

"""This personalized widget is used to create both terminals of the server, one LabelText is composed of one text, one label
 and some methods to deal with them."""

class LabelText(Frame):
    def __init__(self,boss, label_txt, text_txt, editable = False):
        Frame.__init__(self,boss)

        self.label = Label(self, text=label_txt)
        self.label.pack()

        self.text = Text(self, bd =5)
        self.text.insert("1.0", text_txt)
        if(not editable):
            self.text.config(state = DISABLED)
        self.text.pack()

    def get(self):
        return self.text.get('1.0',END)

    def update_display(self, data):
        self.text.config(state = NORMAL)
        #self.text.delete("1.0",END)
        self.text.insert(END, "\n" +data)
        self.text.config(state = DISABLED)

    def clear_display(self):
        self.text.config(state=NORMAL)
        self.text.delete("1.0",END)

    def clear(self):
        self.text.delete("1.0", END)

if __name__ == '__main__':
    fen = Tk()
    box1 = LabelText(fen,"Test du label","Test du texte", True)
    box2 = LabelText(fen,"Test du label (2)", "Test du texte (2)")
    box1.grid(row = 1, column = 1)
    box2.grid(row = 1, column = 2)
    box1.clear_display()

    fen.mainloop()