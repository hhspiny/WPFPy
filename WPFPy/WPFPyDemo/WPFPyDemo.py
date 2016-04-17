#import wpf
#from System.Windows import Application, Window
import clr, System
import WPFPy
# windows class has to be the first class for VS to add event automatically
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
            self.VM.VMoutputText = self.VM.VMinputText + "\n" + self.window.Title
    
    def textBox_input_LostFocus(self, sender, e):
        self.VM.VMoutputText = "lost focus"
   

class MyViewModel(WPFPy.DotNetExpandoObject):
    def __init__(self):
        super(MyViewModel,self).__init__()
        self.VMinputText = "Line - in"
        self.VMoutputText = "Line - out"
        # register eventhandler for DataContext changed event -- after all data binding are initialized
        self.addPropertyChanged(self.dataContextChanged)

    def dataContextChanged(self,s,e):
        if e.PropertyName == "VMinputText":
            self.VMoutputText = self.VMinputText

if __name__ == '__main__':
#    Application().Run(MyWindow())

     vm = MyViewModel()
     w1 = MyWindow(ownThread=True, viewModel = vm)
     w1.changeWindowTitle("Window - 1")

     @WPFPy.Window.windowThread
     def getTitle(self):
        return self.window.Title
#     print getTitle(w1)

     
     
