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

    def initDataBinding(self):
        super(WPFPyFrameWork,self).initDataBinding()
        self.dataContext.textBlock = "First Text-1"      
        self.dataContext.textBox = "Line - 1" 
        self.dataContext.label = " Initial "
   
    def customizeWindow(self):
    # override base class method, execute in self.window thread context
        super(WPFPyFrameWork,self).customizeWindow()
        self.controls.button.Click += self.buttonClick
        self.controls.button1.Click += self.button1Click
        self.controls.button2.Click += self.button2_Click

    def dataContextChanged(self, s, e):
        super(WPFPyFrameWork, self).dataContextChanged(s, e)
        tmpText = '''
Auto_Change
Title: Title=%s
textBlock.Control=%s
textBlock.Data=%s
textBox.Control=%s
textBox.Data=%s
''' %(
            self.window.Title,
            self.controls.textBlock.Text,
            self.dataContext.textBlock,
            self.controls.textBox.Text,
            self.dataContext.textBox
            )
        if e.PropertyName != 'label':
            self.dataContext.label = tmpText

#  ====  control action target method  ====
    def buttonClick(self, s,e):
        ''' modifiy window via direct access to object
        '''
        self.window.Title = "Second Title"
        self.controls.textBlock.Text = "Second Text : " + self.window.Title
        self.controls.textBox.Text = "Line - 2"

    def button1Click(self, s, e):
         ''' modify window via data binding, be careful, do not assign new object
         '''

         self.dataContext.textBlock = "Third Text"
         self.dataContext.textBox = "Line - 3"

    def button2_Click(self, sender, e):
        tmpText = '''
Click_Change
Title: Title=%s
textBlock.Control=%s
textBlock.Data=%s
textBox.Control=%s
textBox.Data=%s
''' %(
            self.window.Title,
            self.controls.textBlock.Text,
            self.dataContext.textBlock,
            self.controls.textBox.Text,
            self.dataContext.textBox
            )
        self.dataContext.label = tmpText

#  ===   public method to access window property, method, need to have @WPFWindow.WPFWindowThread decorator
    @WPFWindow.WPFWindowThread
    def changeWindowTitle(self, text1, text2):
        ''' outside method to change directly via control
        ''' 
        self.window.Title = text1 + text2
        self.controls.textBlock.Text = "Outside - 1 : " + text1 + text2

    @WPFWindow.WPFWindowThread
    def changeWindowTitle2(self, text1, text2):
         ''' outside method to change directly via data binding
         ''' 
         self.dataContext.textBlock = "Outside - 2 : " + text1 + text2
    

            
def run():
        import WPFPyFrameWork
        global myMainWindow1
        global myMainWindow2
        myMainWindow1 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
#        Threading.Thread.Sleep(18000)
#        myMainWindow1.changeWindowTitle("Window ","1")
#        Threading.Thread.Sleep(18000)
#        myMainWindow1.changeWindowTitle2("Window ","2")

#        myMainWindow2 = WPFPyFrameWork.WPFPyFrameWork(show=True , ownThread = True, attachThread = False,  modal = False)
#        myMainWindow2.changeWindowTitle("Window ","2")
        
        @WPFWindow.WPFWindowThread
        def modifyWindowTitle(self, text):
            self.window.Title = text
            self.controls.button.Text = "Modified by Main Program"

#        ModifyWindowTitle(myMainWindow1, "Modified by Main Program")

        return myMainWindow1

if __name__ == "__main__":
        w = run()
        myMainWindow1.thread.Join()