#import wpf
#from System.Windows import Application, Window
import clr, System
import WPFPy

class MyViewModel(WPFPy.DotNetINotifyPropertyChanged):
    __namespace__ = "viewModel"
    def __init__(self):
        super(MyViewModel,self).__init__()
            # test code
        self._inputText = "Line - in"
        self._outputText = "Line - out"
    @clr.clrproperty(str)
    def inputText(self):
        return self._inputText
    @inputText.setter
    def inputText(self,value):
        self._inputText = value
        self.OnPropertyChanged("inputText") 
    @clr.clrproperty(str)
    def outputText(self):
        return self._outputText
    @outputText.setter
    def outputText(self,value):
        self._outputText = value
        self.OnPropertyChanged("outputText")
    # test code

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

    def initDataBinding(self):
        super(MyWindow, self).initDataBinding()

    def dataContextChanged(self, s, e):
        super(MyWindow, self).dataContextChanged(s, e)
        if e.PropertyName == "inputText":
            self.dataContext.outputText = self.dataContext.inputText

if __name__ == '__main__':
#    Application().Run(MyWindow())

     vm = MyViewModel()
     def callback(s,e):
          print "callback"

     w1 = MyWindow(ownThread=True, viewModel = vm)
     w1.changeWindowTitle("Window - 1")

     @WPFPy.Window.windowThread
     def getTitle(self):
        return self.window.Title
     print getTitle(w1)

     
     
