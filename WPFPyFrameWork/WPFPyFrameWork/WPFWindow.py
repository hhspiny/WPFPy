# define base class framework for Python.Net interface with WPF

import clr, System
clr.AddReference(r"wpf\PresentationFramework")
from System import IO, Windows, Threading
from System import TimeSpan

class WPFWindow(object):
    """
    Wrapper class for Systems.Window.Window class. Create and save WPF/XAML window in Window attribute
    All member functions and attributes can be directly accessed regardless of thread. The wrapper class
    automatically use the proper mechanism to handle messaging neccessary between different threads
    """
    
    def __init__(self, xamlFile=None, show=True , ownThread = False, attachThread = False, modal = False):
        """ xamlFile:   xamlFile to create Window object
            show:       show the window during construction
            ownThread:  create a separate thread for this window
            attachThread: attach to the created window thread
            modal:      block input of other windows (in the same thread)
        """
        self.XamlFile=xamlFile
        self.ownThread = ownThread
        self.attachThread = attachThread
        self.modal = modal
        self.show = show
        if self.ownThread:
            self.CreateThread()
        else:
            self.InitWindow()

    def InitWindow(self):
        ''' initialize window by creating window object from xaml file and call rest init methods
        thread aware 
        '''
        try:
            self.XamlStream = IO.StreamReader(self.XamlFile)
            self.Window =  Windows.Markup.XamlReader.Load(self.XamlStream.BaseStream)
        except System.Windows.Markup.XamlParseException as e:
        # need to test what exception gets thrown and print information
            print "Error parsing XAML file %s" % self.XamlFile
            raise

        if self.ownThread:
            # check if current thread has a sync_context, if not create one        
            self.SyncContext = Threading.SynchronizationContext.Current
            if self.SyncContext == None:
                self.SyncContext =  Windows.Threading.DispatcherSynchronizationContext(Windows.Threading.Dispatcher.CurrentDispatcher)
                Threading.SynchronizationContext.SetSynchronizationContext(self.SyncContext)    
            # add window close measurement  
            self.Window.Closed += self.ThreadShutdown

        if self.show: 
            if self.modal:
                self.Window.ShowDialog()
            else:
                self.Window.Show()
        self.InitControls()
        self.InitCustomizeControls()
        
        if self.ownThread:
            # notify that window creation completed
            self.evt.Set()

    def InitControls(self):
        """ default behaviors to initialize windows, called during class construction """
        pass

    def InitCustomizeControls(self):
        """ abstract class to be overridden by child class, customized window initialization during construction"""
        pass

# the following methods handle when the window requires its own thread 

    def CreateThread(self):
        ''' create a separate thread for the window during construction '''
        self.evt = Threading.AutoResetEvent(False)
        self.Thread = Threading.Thread(Threading.ThreadStart(self.ThreadStart))
        self.Thread.IsBackground = True
        self.Thread.SetApartmentState(Threading.ApartmentState.STA)
        self.Thread.Start()
        # wait for window creation before continue
        self.evt.WaitOne() 
        # block calling thread or not
        if self.attachThread:
           self.Thread.Join()
        return self.Thread

    def ThreadStart(self):
        ''' start the thread to intialize window'''
        self.InitWindow()
        if Windows.Application.Current == None:
            self.Application = Windows.Application()
            self.Application.Run()
        else:
            Windows.Threading.Dispatcher.Run()

    def ThreadShutdown(self,s,e):
        # shuts down the Dispatcher when the window closes
        Windows.Threading.Dispatcher.CurrentDispatcher.BeginInvokeShutdown(Windows.Threading.DispatcherPriority.Background)      

    # two functions below will execute function in the window object's own thread
    def PostToUIThread(self,func, arg=None):
        ''' Post a function "func" to window's thread with "arg" as single parameter object
        alternative,use class attribute to pass to and return value from "func"
            Post: execute in sync with original thread, and returne exception to original thread
        ''' 
        self.SyncContext.Post( Threading.SendOrPostCallback(func), arg )

    def SendToUIThread(self,func, arg=None):
        ''' Send a function "func" to window's thread with "arg" as single parameter object
        alternative,use class attribute to pass to and return value from "func"
            Send: execute in async with original thread, and exception remains in Window thread
        ''' 
        self.SyncContext.Send( Threading.SendOrPostCallback(func), arg )


# members below can potentially be called from other thread, need built-in thread messaging system

    def __getattr__(self, item):
        """ for attributes that are missing (by __getattribute__) construct from Window object """
        tmp = self.Window.FindName(item)
        if tmp == None:
            raise AttributeError("%s does not have % attribute/control" %(self.Window.Title, item))
        else:
            return self.Window.FindName(item)
      

