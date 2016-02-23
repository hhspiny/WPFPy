#import wpf

#from System.Windows import Application, Window

#class MyWindow(Window):
#    def __init__(self):
#        wpf.LoadComponent(self, 'WPFPyFrameWork.xaml')
    

#if __name__ == '__main__':
#    Application().Run(MyWindow())

import clr
from WPFWindow import *
from System import TimeSpan, Windows, Threading

class WPFPyFrameWorkViewModel(WPFViewModel):
    def __init__(self, w):
        super(WPFPyFrameWorkViewModel, self).__init__(w)
        self.textBlockContent = "Window "+ self.WPFWindow.Window.Title

class MyData(System.Object):
   def __init__(self):
      self.text = 'Initial text'
   @property
   def Mine(self): 
        print "here"
        return self.text
   @Mine.setter
   def Mine(self, value): 
        print "2"
        self.text = value

class WPFPyFrameWork(WPFWindow):
    def __init__(self,                          show=True , 
                                                ownThread = False, 
                                                attachThread = False, 
                                                modal = False):

        super(WPFPyFrameWork, self).__init__(xamlFile = "WPFPyFrameWork.xaml", 
                                                show=show , 
                                                ownThread = ownThread, 
                                                attachThread = attachThread, 
                                                modal = modal)

    def __InitDataContext__(self):
#        self.ViewModel =  WPFPyFrameWorkViewModel(self)
#        self.Window.textBlockContent = "Window "+ self.Window.Title
        student = MyData()
        self.Window.DataContext = student
        

    def __InitCustomizeControls__(self):
    # override base class method, execute in self.Window thread context
            self.Controls.button.Click += self.ButtonClick

    def ButtonClick(self, s,e):
        self.Controls.textBlock.Text = "clicked by " + self.Window.Title
    
    # any function that operates on self.Window that can be called from outside Window Thread
    # should have @WPFWindow.WPFWindowThread decorator
    @WPFWindow.WPFWindowThread
    def ChangeWindowTitle(self, text1, text2):
        self.Window.Title = text1 + text2
        return self.Window.Title
    
def run():
        import WPFPyFrameWork
        global myMainWindow1
        global myMainWindow2
        myMainWindow1 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
        print myMainWindow1.ChangeWindowTitle("Window ","1")
        myMainWindow2 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
        print myMainWindow2.ChangeWindowTitle("Window ","2")
        
        @WPFWindow.WPFWindowThread
        def ModifyWindowTitle(self, text):
            self.Window.Title = text
            self.Controls.button.Text = "Now"

        ModifyWindowTitle(myMainWindow1, "modified")

        return myMainWindow1

if __name__ == "__main__":
        w = run()
        myMainWindow1.Thread.Join()