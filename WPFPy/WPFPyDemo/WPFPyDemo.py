#import wpf
#from System.Windows import Application, Window
import clr, System
import WPFPy

class MyViewModel(WPFPy.DotNetExpandoObject):
    def __init__(self):
        super(MyViewModel,self).__init__()
        self.inputText = "Line - in"
        self.outputText = "Line - out"
        # register eventhandler for DataContext changed event -- after all data binding are initialized
        self.addPropertyChanged(self.dataContextChanged)

    def dataContextChanged(self,s,e):
        if e.PropertyName == "inputText":
            self.outputText = self.inputText

class MyWindow(WPFPy.Window):
    def __init__(self, ownThread = False, attachThread = False, viewModel = None):
#        wpf.LoadComponent(self, 'WPFPyDemo.xaml')
        super(MyWindow, self).__init__("WPFPyDemo.xaml", 
                ownThread = ownThread, attachThread=attachThread,
                viewModel = viewModel)   

    @WPFPy.Window.windowThread
    # function exposed to outside of thread access
    def changeWindowTitle(self, title):
        self.window.Title = title
    
    def display_button_Click(self, sender, e):
#        self.VM.outputText = "Changed"
            self.VM.outputText = self.VM.inputText + "\n" + self.window.Title

if __name__ == '__main__':
#    Application().Run(MyWindow())

     vm = MyViewModel()
     w1 = MyWindow(ownThread=True, viewModel = vm)
     w1.changeWindowTitle("Window - 1")

     @WPFPy.Window.windowThread
     def getTitle(self):
        return self.window.Title
#     print getTitle(w1)

     
     
