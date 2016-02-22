# define base class framework for Python.Net interface with WPF

import clr, System
clr.AddReference(r"wpf\PresentationFramework")
from System import IO, Windows, Threading
from System import TimeSpan


class __WPFControlsInWindow__(System.Object):
    ''' surrogate for controls in self.Window in WPFWindow to access controls by name
    '''
    def __init__(self, window):
        self.Window = window

    def __getattr__(self, name):
        control = self.Window.FindName(name)
        if control == None:
            raise AttributeError("%s does not have %s attribute/control" % (self.Window.Title, name))
        else:
            return control
    
class WPFWindow(System.Object):
    """
    Wrapper class for Systems.Window.Window class. Create and save WPF/XAML window in self.Window 
    Since self.Window could operate in separate thread, all externally accessible functions that could 
    reference self.Window should be through functions with decorator @WPFWindow.WPFWindowThread
    """
    
    def __init__(self, application=None, xamlFile=None, show=True , ownThread = False, attachThread = False, modal = False):
        """ xamlFile:   xamlFile to create Window object
            show:       show the window during construction
            ownThread:  create a separate thread for this window
            attachThread: attach to the created window thread
            modal:      block input of other windows (in the same thread)
        """
        self.XamlFile=xamlFile
        self.ownThread = ownThread
        self.attachThread = attachThread
        self.__ModalWindow__ = modal
        self.__ShowWindow__ = show
        self.Application = application
        if self.ownThread:
            self.__CreateThread__()
        else:
            self.__InitWindow__()

    def __InitWindow__(self):
        ''' initialize window by creating window object from xaml file and call rest init methods '''
        try:
            XamlStream = IO.StreamReader(self.XamlFile)
            self.Window =  Windows.Markup.XamlReader.Load(XamlStream.BaseStream)
            self.Controls = __WPFControlsInWindow__(self.Window)
        except System.Windows.Markup.XamlParseException as e:
        # need to test what exception gets thrown and print information
            print "Error parsing XAML file %s" % self.XamlFile
            raise

        if self.__ShowWindow__: 
            if self.__ModalWindow__:
                self.Window.ShowDialog()
            else:
                self.Window.Show()
        self.__InitControls__()
        self.__InitCustomizeControls__()
        
    def __InitControls__(self):
        """ default behaviors to initialize windows, called during class construction """
        pass

    def __InitCustomizeControls__(self):
        """ abstract class to be overridden by child class, customized window initialization during construction"""
        pass

# the following methods handle when the window requires its own thread 

    def __CreateThread__(self):
        ''' create a separate thread for the window during construction '''
        self.__evt = Threading.AutoResetEvent(False)
        self.Thread = Threading.Thread(Threading.ThreadStart(self.__ThreadStart__))
        self.Thread.IsBackground = True
        self.Thread.SetApartmentState(Threading.ApartmentState.STA)
        self.Thread.Start()
        # wait for window creation before continue
        self.__evt.WaitOne() 
        # block calling thread or not
        if self.attachThread:
           self.Thread.Join()
        return self.Thread

    def __ThreadStart__(self):
        ''' start the thread to intialize window'''

        # check if current thread has a sync_context, if not create one        
        self.SyncContext = Threading.SynchronizationContext.Current
        if self.SyncContext == None:
            self.SyncContext =  Windows.Threading.DispatcherSynchronizationContext(Windows.Threading.Dispatcher.CurrentDispatcher)
            Threading.SynchronizationContext.SetSynchronizationContext(self.SyncContext)    
        # add window close measurement  
        self.__InitWindow__()
        self.Window.Closed += self.__ThreadShutdown__
        self.__evt.Set()

        if self.Application == None :
            if Windows.Application.Current == None:
                self.Application = Windows.Application()
                self.Application.Run()
            else:
                self.Application = Windows.Application.Current
                Windows.Threading.Dispatcher.Run()
        else:
            Windows.Threading.Dispatcher.Run()

    def __ThreadShutdown__(self,s,e):
        # shuts down the Dispatcher when the window closes
        Windows.Threading.Dispatcher.CurrentDispatcher.BeginInvokeShutdown(Windows.Threading.DispatcherPriority.Background)       

    # any function that operates on self.Window that can be called from outside Window Thread
    # should have @WPFWindow.WPFWindowThread decorator
    # since the function can only operate with a WPFWindow context, the function's first arg should alwasy be
    # WPFWindow object
    @staticmethod
    def WPFWindowThread(func):        ''' decorator function to wrapper calls referencing self.Windo in thread safe call '''        def wrapper(self, *args, **kwargs):        # wrapper function to run within correct thread context of WPFWindow object (farg)            def delegate(param):            # the delegate function to be executed in self.Window Thread            # since delegate() is defined with context of self.wrapper, it automatically has access to self                retval = func(self, *(self._msg[0]),**(self._msg[1]))
                self._msg[2] = retval                        # use self._msg to pass on parameters to delegate function            self._msg = [args, kwargs, None]            if Threading.SynchronizationContext.Current == self.SyncContext:            #   executing in WPFWindow's context                delegate(None)                retval =  self._msg[2]                return retval            else:            #  send delegate function to proper context                self.SyncContext.Send( Threading.SendOrPostCallback(delegate), None)                retval =  self._msg[2]                return retval        return wrapper      