# define base class framework for Python.Net interface with WPF

import clr, System
clr.AddReference(r"wpf\PresentationFramework")
from System import IO, Windows, Threading
from System import TimeSpan

from functools import wraps

class WPFWindow(object):
    """
    Wrapper class for Systems.Window.Window class. Create and save WPF/XAML window in self.Window
    Automatically looks up missing members as members of self.Window, and handles Window thread messaging. 
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
        self.__ModalWindow = modal
        self.__ShowWindow = show
        if self.ownThread:
            self.CreateThread()
        else:
            self.InitWindow()

    def InitWindow(self):
        ''' initialize window by creating window object from xaml file and call rest init methods '''
        try:
            self.XamlStream = IO.StreamReader(self.XamlFile)
            self.Window =  Windows.Markup.XamlReader.Load(self.XamlStream.BaseStream)
        except System.Windows.Markup.XamlParseException as e:
        # need to test what exception gets thrown and print information
            print "Error parsing XAML file %s" % self.XamlFile
            raise

        if self.__ShowWindow: 
            if self.__ModalWindow:
                self.Window.ShowDialog()
            else:
                self.Window.Show()
        self.InitControls()
        self.InitCustomizeControls()
        
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

        # check if current thread has a sync_context, if not create one        
        self.SyncContext = Threading.SynchronizationContext.Current
        if self.SyncContext == None:
            self.SyncContext =  Windows.Threading.DispatcherSynchronizationContext(Windows.Threading.Dispatcher.CurrentDispatcher)
            Threading.SynchronizationContext.SetSynchronizationContext(self.SyncContext)    
        # add window close measurement  
        self.InitWindow()
        self.Window.Closed += self.ThreadShutdown
        self.evt.Set()

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
       
#  For attributes not found in wrapper class, look them up in self.Window 
#  automatically handle the need of thread msg passing and pass back wrapper functions if needed

    def __getattr__(self, name):
        return self.__WindowAttribute(self, name)

    def __ResolveWindowMsgType(self, name):
        '''Resolve what 'name' represent in self.window context'''
        self.__WindowThreadMsg = {}
        try:
            # check if attributes or method of self.Windows
            attr = self.Window.__getattribute__(name)
            if callable(attr):
                self.__WindowThreadMsg['type'] = 'func'
            else:
                self.__WindowThreadMsg['type'] = 'attr'
        except AttributeError:
                #check if a control of self.Window
                control = self.Window.FindName(name)
                if control == None:
                    raise AttributeError("%s Window has no attribute or controls with name %s" % (self.Window.Title, NameError))
                self.__WindowThreadMsg['type'] = 'control'

    def __WindowAttribute(self,name):
        ''' Look up attributes in self.Window and handle the thread messaging if neccessary 
        tips:  1. embedded funcs already have access to self namespace
               2. use func(*args, **kwargs) to call funcs with unknown parameter list
        '''

        if self.SyncContext == Threading.SynchronizationContext.Current:
            self.__ResolveWindowMsgType(name)
            if self.__WindowThreadMsg['type'] == 'attr':
                return self.Window.__getattribute__(name)
            elif self.__WindowThreadMsg['type'] == 'control':
                return self.Window.FindName(name)
            elif self.__WindowThreadMsg['type'] == 'func':
                attr = self.Window.__getattribute__(name)
                def wrapper(*args, **kwargs):
                # embedded function, already have access to self namespace
                        retval = attr(*args, **kwargs)
                        return retval
                return wrapper
        else:
            # all reference to self.Window needs to be posted to its own thread
            # first find out if it is attribute, saved in self.__WindowThreadMsg
            self.SyncContext.Send(Threading.SendOrPostCallback(self.__ResolveWindowMsgType), name )
            if self.__WindowThreadMsg['type'] == 'attr':
                pass
            elif self.__WindowThreadMsg['type'] == 'control':
                pass
            elif self.__WindowThreadMsg['type'] == 'func':  
                def delegate(name):
                # delegate function to execute actual self.Window methods in its own thread
                    attr = self.Window.__getattribute__(name)
                    retval = attr(*(self.__WindowThreadMsg['args']), **(self.__WindowThreadMsg['kwargs']))
                    self.__WindowThreadMsg['retval'] = retval
                def wrapper(*args, **kwargs):
                # embedded function, already have access to self namespace                    
                    self.__WindowThreadMsg['args'] = args
                    self.__WindowThreadMsg['kwargs'] = kwargs
                    self.__WindowThreadMsg['retval'] = []
                    self.SyncContext.Send( Threading.SendOrPostCallback(delegate), name )
                    return  self.__WindowThreadMsg['ret']

       