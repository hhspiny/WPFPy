#import wpf

#from System.Windows import Application, Window

#class MyWindow(Window):
#    def __init__(self):
#        wpf.LoadComponent(self, 'WPFPyFrameWork.xaml')
    

#if __name__ == '__main__':
#    Application().Run(MyWindow())

import clr
from WPFWindow import *
from System import TimeSpan, Windows, Threading, Dynamic 


class WPFPyFrameWork(WPFWindow):
    def __init__(self, 
                 viewModel = None, application = None,
                 ownThread = False, attachThread = False,
                 show=True ,modal = False):

        super(WPFPyFrameWork, self).__init__("WPFPyFrameWork.xaml",
                 viewModel = viewModel, application = application,
                 ownThread = ownThread, attachThread = attachThread,
                 show=show ,modal = modal)

    def DefineDataBinding(self):
        super(WPFPyFrameWork,self).DefineDataBinding()
        self.VM.Data.Title = self.VM.BindingTo("Title",System.Text.StringBuilder("First Title"))
        self.VM.Data.Title.Clear()      
        self.VM.Data.Title.Append("Second Title")
        print "now change"
        self.VM.Data.Title = "Third Title"
                 
    def CustomizeWindow(self):
    # override base class method, execute in self.Window thread context
        super(WPFPyFrameWork,self).CustomizeWindow()
        self.Controls.button.Click += self.ButtonClick


#  ====  control action target method  ====
    def ButtonClick(self, s,e):
        self.Controls.textBlock.Text = "clicked by " + self.Window.Title
    
#  ===   public method to access window property, method, need to have @WPFWindow.WPFWindowThread decorator
    @WPFWindow.WPFWindowThread
    def ChangeWindowTitle(self, text1, text2):
        self.Window.Title = text1 + text2
        return self.Window.Title
    
def run():
        import WPFPyFrameWork
        global myMainWindow1
        global myMainWindow2
        myMainWindow1 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
        myMainWindow1.ChangeWindowTitle("Window ","1")
#        myMainWindow2 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
#        myMainWindow2.ChangeWindowTitle("Window ","2")
        
        @WPFWindow.WPFWindowThread
        def ModifyWindowTitle(self, text):
            self.Window.Title = text
            self.Controls.button.Text = "Modified by Main Program"

        ModifyWindowTitle(myMainWindow1, "Modified by Main Program")

        return myMainWindow1

if __name__ == "__main__":
        w = run()
        myMainWindow1.Thread.Join()