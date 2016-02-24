# define base class framework for Python.Net interface with WPF

import clr, System
clr.AddReference(r"wpf\PresentationFramework")
from System import IO, Windows, Threading, ComponentModel
from System import TimeSpan


class WPFControlsInWindow(System.Object):
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

class WPFViewModelData(System.Object):
    ''' class to save all data binding to xaml, attributes can not be re-assigned to other references'''
    def __init__(self):
        pass

        
class WPFViewModel(System.Object):
    ''' surrogate for DataContext in format of ExpandoObject '''
    def __init__(self, window):
        self.DataContext = System.Dynamic.ExpandoObject()
        self.Window = window
        self.Data = WPFViewModelData()

    def BindingTo(self, name, obj):
        ''' create a new attribute and bind the passed on object to the new attribute '''
        if not hasattr(self.Data, name):
            setattr(self.Data, name, obj)
        obj = getattr(self.Data, name)    
        System.Collections.Generic.IDictionary[System.String, System.Object].Add(self.DataContext, name, obj)  
        return obj

class WPFWindow(System.Object):
    """
    Wrapper class for Systems.Window.Window class. 
    1. Create and save WPF/XAML window in self.Window 
    2. All methods that could access self.Window should be defined with decorator @WPFWindow.WPFWindowThread
    3. DataContext/ViewModel Binding process 
    """
    
    def __init__(self, xamlFile,
                 viewModel = None, application = None,
                 ownThread = False, attachThread = False,
                 show=True ,modal = False):
        """ xamlFile:   xamlFile to create Window object
            viewModel: provided WPFViewModel that contains DataContext, if None auto-create with base class
            application: provided Application, if None auto-create with base class
            ownThread:  create a separate thread for this window
            attachThread: attach to the created window thread
            show:       show the window during construction
            modal:      block input of other windows (in the same thread)
        """
        self.XamlFile=xamlFile
        self.VM = viewModel
        self.Application = application
        self.ownThread = ownThread
        self.attachThread = attachThread
        self.Modal = modal
        self.ShowWindow = show

        if self.ownThread:
            self.CreateThread()
        else:
            self.InitWindow()

    def InitWindow(self):
        ''' initialize window by creating window object from xaml file and call rest init methods '''
        try:
            XamlStream = IO.StreamReader(self.XamlFile)
            self.Window =  Windows.Markup.XamlReader.Load(XamlStream.BaseStream)
        except System.Windows.Markup.XamlParseException as e:
        # need to test what exception gets thrown and print information
            print "Error parsing XAML file %s" % self.XamlFile
            raise

        if self.ShowWindow: 
            if self.Modal:
                self.Window.ShowDialog()
            else:
                self.Window.Show()
        self.InitControls()
        self.CustomizeWindow()
        self.CreateDataContext()

    def InitControls(self):
        ''' initialize controls '''
        # to access controls in self.Windows
        self.Controls =WPFControlsInWindow(self.Window)

    def CustomizeWindow(self):
        ''' to be overriden, customize window before launching'''
        pass

    def CreateDataContext(self):
        ''' create DataContext object and attach'''
        if self.VM == None:
            self.VM = WPFViewModel(self)
        self.VM.Window = self
        self.Window.DataContext = self.VM.DataContext
        self.DefineDataBinding()

    def DefineDataBinding(self):
        ''' to be overriden, define individual control data binding targets from xaml'''
        pass


# the following methods handle when the window requires its own thread 

    def CreateThread(self):
        ''' create a separate thread for the window during construction '''
        self.__evt = Threading.AutoResetEvent(False)
        self.Thread = Threading.Thread(Threading.ThreadStart(self.ThreadStart))
        self.Thread.IsBackground = True
        self.Thread.SetApartmentState(Threading.ApartmentState.STA)
        self.Thread.Start()
        # wait for window creation before continue
        self.__evt.WaitOne() 
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

    def ThreadShutdown(self,s,e):
        # shuts down the Dispatcher when the window closes
        Windows.Threading.Dispatcher.CurrentDispatcher.BeginInvokeShutdown(Windows.Threading.DispatcherPriority.Background)       

    # Any functions that could access self.Window should have the WPFWindowThread decorator to pass msg between threads
    # The function can be a class method or a global method, as long as it has first arg is a WPFWindow object
    @staticmethod
    def WPFWindowThread(func):
        ''' decorator to wrapper calls referencing self.Windo in thread safe call, the function itself should have WPFWindow object as first arg '''
        def wrapper(self, *args, **kwargs):
        # wrapper function to run within correct thread context of WPFWindow object (farg)
            def delegate(param):
            # the delegate function to be executed in self.Window Thread
            # since delegate() is defined with context of self.wrapper, it automatically has access to self
                retval = func(self, *(self._msg[0]),**(self._msg[1]))
                self._msg[2] = retval
            
            # use self._msg to pass on parameters to delegate function
            self._msg = [args, kwargs, None]
            if Threading.SynchronizationContext.Current == self.SyncContext:
            #   executing in WPFWindow's context
                delegate(None)
                retval =  self._msg[2]
                return retval
            else:
            #  send delegate function to proper context
                self.SyncContext.Send( Threading.SendOrPostCallback(delegate), None)
                retval =  self._msg[2]
                return retval
        return wrapper      