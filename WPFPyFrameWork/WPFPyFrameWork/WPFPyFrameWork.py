#import wpf

#from System.Windows import Application, Window

#class MyWindow(Window):
#    def __init__(self):
#        wpf.LoadComponent(self, 'WPFPyFrameWork.xaml')
    

#if __name__ == '__main__':
#    Application().Run(MyWindow())

import WPFPyBase
from System import TimeSpan, Windows, Threading

class WPFPyFrameWork(WPFPyBase.WPFPyBase):
    def __init__(self, block=True):
        super(WPFPyFrameWork, self).__init__("WPFPyFrameWork.xaml", block)

# ==
# execute within self.Window thread context
# ==

    def InitCustomizeControls(self):
    # override base class method, execute in self.Window thread context
        try:
            self.GetControl("textBlock").Text = "Window "+self.MainWindow.Title
            tmpCtrl = self.GetControl("button")
            tmpCtrl.Click +=self.ButtonClick
        except AttributeError as e:
            print str(e)

    def ButtonClick(self, s,e):
        self.GetControl('textBlock').Text = "clicked by " + self.MainWindow.Title
        def delegate(param):
            myMainWindow1.GetControl('textBlock').Text = "clicked by %s" % param
        myMainWindow1.SendToUIThread(delegate, self.MainWindow.Title)
      
# == 
# execute outside self.Window thread context
# ==
    def ChangeWindowTitle(self, text1, text2):
        self.param = [text1, text2,None]
        self.ret = None
        def delegate(param):
            self.MainWindow.Title = self.param[0] + self.param[1]
            self.ret = self.MainWindow.Title
        self.SendToUIThread(delegate)
        return self.ret
    
def run():
    w = WPFPyBase.WPFPyWindow("WPFPyFrameWork.xaml")
    Windows.Application().Run()

if __name__ == "__main__":
        thread = Threading.Thread(Threading.ThreadStart(run))
        thread.IsBackground = True
        thread.SetApartmentState(Threading.ApartmentState.STA)
        thread.Start()
        thread.Join()