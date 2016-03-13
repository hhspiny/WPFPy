#import wpf
#from System.Windows import Application, Window
import clr, System
import WPFPy

class MyWindow(WPFPy.Window):
    def __init__(self, ownThread = False, attachThread = False):
#        wpf.LoadComponent(self, 'WPFPyDemo.xaml')
        super(MyWindow, self).__init__("WPFPyDemo.xaml", ownThread = ownThread, attachThread=attachThread)   

    @WPFPy.Window.windowThread
    # function exposed to outside of thread access
    def changeWindowTitle(self, title):
        self.window.Title = title
    
    def display_button_Click(self, sender, e):
            self.dataContext.outputText = self.dataContext.inputText + "\n" + self.window.Title

    def initDataBinding(self):
        super(MyWindow, self).initDataBinding()
        self.dataContext.inputText = "Line - 1"
        self.dataContext.outputText = "Init Output"

    def dataContextChanged(self, s, e):
        super(MyWindow, self).dataContextChanged(s, e)
        print s, e
        if e.PropertyName == "inputText":
            self.dataContext.outputText = self.dataContext.inputText

if __name__ == '__main__':
#    Application().Run(MyWindow())

     w1 = MyWindow(ownThread=True)
     w1.changeWindowTitle("Window - 1")

#     w2 = MyWindow(ownThread=True)
#     w2.changeWindowTitle("Window - 2")

     @WPFPy.Window.windowThread
     def getTitle(self):
        return self.window.Title
#     print getTitle(w1)

     
     
