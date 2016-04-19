#import wpf
#from System.Windows import Application, Window
import clr, System
import WPFPy

# windows class has to be the first class for VS to add event automatically
class MyWindow(WPFPy.Window):
    def __init__(self, ownThread = False, attachThread = False, viewModel = None):
        super(MyWindow, self).__init__("WPFPyDemo.xaml", 
                ownThread = ownThread, attachThread=attachThread,
                viewModel = viewModel)   

    @WPFPy.Window.windowThread
    # function exposed to outside of thread access
    def changeWindowTitle(self, title):
        self.window.Title = title
    
    def display_button_Click(self, sender, e):
#        self.VM.outputText = "Changed"
            self.VM.VMoutputText = self.VM.VMinputText + "\n" + self.window.Title
    
    def textBox_input_LostFocus(self, sender, e):
        self.VM.VMoutputText = "lost focus"
   

class MyViewModel(WPFPy.ViewModel):
    def __init__(self):
        super(MyViewModel,self).__init__()

    def initData(self):
        super(MyViewModel,self).initData()
        self.VMinputText = "Line - in"
        self.VMoutputText = "Line - out"
        self.VMlistBox = ["item-1", "item-2"]

    def dataContextChanged(self,s,e):
        super(MyViewModel,self).dataContextChanged(s,e)
        if e.PropertyName == "VMinputText":
            self.VMoutputText = self.VMinputText

if __name__ == '__main__':
     vm = MyViewModel()
     w1 = MyWindow(ownThread=True, viewModel = vm)

     # define a function to directly access window's attributes from main thread
     @WPFPy.Window.windowThread
     def getTitle(self):
        return self.window.Title
#     print getTitle(w1)

     
     
