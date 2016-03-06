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

    def InitDataBinding(self):
        super(WPFPyFrameWork,self).InitDataBinding()
        self.DataContext.textBlock = "First Text-1"      
        self.DataContext.textBox = "Line - 1" 
        self.DataContext.label = " Initial "
   
    def CustomizeWindow(self):
    # override base class method, execute in self.Window thread context
        super(WPFPyFrameWork,self).CustomizeWindow()
        self.Controls.button.Click += self.ButtonClick
        self.Controls.button1.Click += self.Button1Click
        self.Controls.button2.Click += self.button2_Click

    def DataContextChanged(self, s, e):
        super(WPFPyFrameWork, self).DataContextChanged(s, e)
        tmpText = '''
Auto_Change
Title: Title=%s
textBlock.Control=%s
textBlock.Data=%s
textBox.Control=%s
textBox.Data=%s
''' %(
            self.Window.Title,
            self.Controls.textBlock.Text,
            self.DataContext.textBlock,
            self.Controls.textBox.Text,
            self.DataContext.textBox
            )
        if e.PropertyName != 'label':
            self.DataContext.label = tmpText

#  ====  control action target method  ====
    def ButtonClick(self, s,e):
        ''' modifiy window via direct access to object
        '''
        self.Window.Title = "Second Title"
        self.Controls.textBlock.Text = "Second Text : " + self.Window.Title
        self.Controls.textBox.Text = "Line - 2"

    def Button1Click(self, s, e):
         ''' modify window via data binding, be careful, do not assign new object
         '''

         self.DataContext.textBlock = "Third Text"
         self.DataContext.textBox = "Line - 3"

    def button2_Click(self, sender, e):
        tmpText = '''
Click_Change
Title: Title=%s
textBlock.Control=%s
textBlock.Data=%s
textBox.Control=%s
textBox.Data=%s
''' %(
            self.Window.Title,
            self.Controls.textBlock.Text,
            self.DataContext.textBlock,
            self.Controls.textBox.Text,
            self.DataContext.textBox
            )
        self.DataContext.label = tmpText

#  ===   public method to access window property, method, need to have @WPFWindow.WPFWindowThread decorator
    @WPFWindow.WPFWindowThread
    def ChangeWindowTitle(self, text1, text2):
        ''' outside method to change directly via control
        ''' 
        self.Window.Title = text1 + text2
        self.Controls.textBlock.Text = "Outside - 1 : " + text1 + text2

    @WPFWindow.WPFWindowThread
    def ChangeWindowTitle2(self, text1, text2):
         ''' outside method to change directly via data binding
         ''' 
         self.DataContext.textBlock = "Outside - 2 : " + text1 + text2
    

            
def run():
        import WPFPyFrameWork
        global myMainWindow1
        global myMainWindow2
        myMainWindow1 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
#        Threading.Thread.Sleep(18000)
#        myMainWindow1.ChangeWindowTitle("Window ","1")
#        Threading.Thread.Sleep(18000)
#        myMainWindow1.ChangeWindowTitle2("Window ","2")

#        myMainWindow2 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
#        myMainWindow2.ChangeWindowTitle("Window ","2")
        
        @WPFWindow.WPFWindowThread
        def ModifyWindowTitle(self, text):
            self.Window.Title = text
            self.Controls.button.Text = "Modified by Main Program"

#        ModifyWindowTitle(myMainWindow1, "Modified by Main Program")

        return myMainWindow1

if __name__ == "__main__":
        w = run()
        myMainWindow1.Thread.Join()