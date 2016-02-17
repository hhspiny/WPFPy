import clr, System
clr.AddReference(r"wpf\PresentationFramework")
from System import IO, Windows, Threading
from System import TimeSpan

#need to do !! define a parent application --> and find other window

#from System.Windows import Application, Window
#from System.Windows.Controls import Button, Canvas, TextBlock
#from System.Windows import LogicalTreeHelper
    
class WPFPyBase(object):
# the base class for all WPF window
# load xaml and create window object

    def __init__(self, xamlFile, block=True):
    # block: whether to block calling thread
        self.XamlFile = xamlFile
        self.Block = block
        self.evt = Threading.AutoResetEvent(False)
        self.Application = None
        self.CreateThread(block)


    def CreateThread(self, block=True):
    # block: whether block return to current thread
        thread = Threading.Thread(Threading.ThreadStart(self.ThreadStart))
        thread.IsBackground = True
        self.Thread = thread
        thread.SetApartmentState(Threading.ApartmentState.STA)
        thread.Start()
        # wait for window creation before continue
        self.evt.WaitOne() 
        # block calling thread or not
        if block:
           thread.Join()
        return self.Thread


    # two functions below will execute function in UIThread, use associated context
    # created during initial window construction. 
    # execute "func" with "arg" parameter: arg parameter is single object (can be a list)
    # to pass parameter and get return, use the default class namespace "self." 
    def PostToUIThread(self,func, arg=None):
    # Post: execute sync, also pass back exception, handled by calling thread
        self.Context.Post( Threading.SendOrPostCallback(func), arg )

    def SendToUIThread(self,func, arg=None):
    # Send:  execute async, will not pass back exceptop, handled by UIThread
        self.Context.Send( Threading.SendOrPostCallback(func), arg )


#  =====
#  Below methods are executed in its own separate thread of created window
#  =====
    def ThreadStart(self):
        self.InitWindow()
        if Windows.Application.Current == None:
            self.Application = Windows.Application()
            self.Application.Run()
        else:
            Windows.Threading.Dispatcher.Run()

    def ThreadShutdown(self,s,e):
        # shuts down the Dispatcher when the window closes
        Windows.Threading.Dispatcher.CurrentDispatcher.BeginInvokeShutdown(Windows.Threading.DispatcherPriority.Background)

    def InitWindow(self):
    # initialization explicitly called from STA environment to read xaml and initialize window
        
        #  forces the synchronization context to be in place before the Window gets created
        #  UI thread is different from the worker thread (calling thread) need context to mashel into UI thread
        self.Context = Threading.SynchronizationContext.Current
        if self.Context == None:
            self.Context =  Windows.Threading.DispatcherSynchronizationContext(Windows.Threading.Dispatcher.CurrentDispatcher)
            Threading.SynchronizationContext.SetSynchronizationContext(self.Context)  
     
        self.Stream = IO.StreamReader(self.XamlFile)
        self.MainWindow = Windows.Markup.XamlReader.Load(self.Stream.BaseStream)
        self.MainWindow.Closed += self.ThreadShutdown
        self.MainWindow.Show()
        # notify window creation completed
        self.evt.Set()
        self.InitControls()
        self.InitCustomizeControls()

    def InitControls(self):
    # default control initiation for all windows
        pass

    def InitCustomizeControls(self):
    # interface allow child class to further customize controls
        pass

    def GetControl(self,name):
        tmp = self.MainWindow.FindName(name)
        if tmp == None:
            raise AttributeError("%s window does not have %s control" % (self.MainWindow.Title, name))
        else:
            return tmp
      

