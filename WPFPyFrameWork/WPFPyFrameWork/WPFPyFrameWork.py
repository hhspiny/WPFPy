#import wpf

#from System.Windows import Application, Window

#class MyWindow(Window):
#    def __init__(self):
#        wpf.LoadComponent(self, 'WPFPyFrameWork.xaml')
    

#if __name__ == '__main__':
#    Application().Run(MyWindow())

import WPFWindow
from System import TimeSpan, Windows, Threading

class WPFPyFrameWork(WPFWindow.WPFWindow):
    def __init__(self,                          show=True , 
                                                ownThread = False, 
                                                attachThread = False, 
                                                modal = False):

        super(WPFPyFrameWork, self).__init__(xamlFile = "WPFPyFrameWork.xaml", 
                                                show=show , 
                                                ownThread = ownThread, 
                                                attachThread = attachThread, 
                                                modal = modal)

    def InitCustomizeControls(self):
    # override base class method, execute in self.Window thread context
        try:
            self.Window.textBlock.Text = "Window "+self.Window.Title
            self.Window.button.Click += self.ButtonClick
        except AttributeError as e:
            print str(e)

    def ButtonClick(self, s,e):
        self.Window.textBlock.Text = "clicked by " + self.Window.Title
      
    def ChangeWindowTitle(self, text1, text2):
        self.param = [text1, text2,None]
        self.ret = None
        def delegate(param):
            self.Window.Title = self.param[0] + self.param[1]
            self.ret = self.Window.Title
        self.SendToUIThread(delegate)
        return self.ret
    
def run():
        import WPFPyFrameWork
        global myMainWindow1
        global myMainWindow2
        myMainWindow1 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
        myMainWindow1.ChangeWindowTitle("Window ","1")
        myMainWindow2 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
        myMainWindow2.ChangeWindowTitle("Window ","2")
        return myMainWindow1


if __name__ == "__main__":
        w = run()
        a = w.Window.Title
        myMainWindow2.Thread.Join()