# define base class framework for Python.Net interface with WPF

import clr, System
clr.AddReference(r"wpf\PresentationFramework")
from System import IO, Windows, Threading, ComponentModel
from System import TimeSpan


class WPFWindowControl(System.Object):
    ''' surrogate for controls in self.Window in WPFWindow to access controls by name
        to overcome difficulty of not able to derive .Net object Windows.Window
        __attr is assumed to be class's own attributes
    '''
    def __init__(self, window):
        self.__Window = window

    def __getattr__(self, name):
        control = self.__Window.FindName(name)
        if control == None:
            raise AttributeError("%s window does not have %s control" % (self.__Window.Title, name))
        else:
            return control

class WPFWindowDataContext(System.Object):
    ''' surrogate for ExpandoObject in self.Window.DataContext to access it via attribute
        to overcome the difficulty of the need to access ExpandoObject via its .Net interface
        __attr is assumed to be the class's own attributes
    '''
    def __init__(self,dataContext):
        self.__DataContext = dataContext

    def __getattr__(self,name):
        if name[0] == '_':
            return self.__getattribute__(name)
        else:
            obj = None
            wrapped = System.Collections.Generic.IDictionary[System.String, System.Object](self.__DataContext)
            ret = wrapped.TryGetValue(name, obj)
            if ret[0]:
                return ret[1]
            else:
                raise AttributeError, "%s has no attribute '%s'" % ("WPFWindow's DataContext", name)
 
    def __setattr__(self,name,obj):
       if name[0] == "_":
        # class's own attribute, do not directly access __dict__ but access base class method to set attribute
            super(WPFWindowDataContext,self).__setattr__(name,obj)
       else:
        # DataContext's attribute
            wrapped = System.Collections.Generic.IDictionary[System.String, System.Object](self.__DataContext)
            if wrapped.ContainsKey(name):
                wrapped.set_Item(name, obj)
            else:
                wrapped.Add(name, obj)
 

class WPFWindow(System.Object):
    """
    Wrapper class for Systems.Window.Window class. 
    1. Create and save WPF/XAML window in self.Window 
    2. All methods that could access self.Window should be defined with decorator @WPFWindow.WPFWindowThread
    3. DataContext/ViewModel Binding process 
    4. self.Window contains the actual WPF window object, but all controls should be access via self.Controls
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
        self.Controls =WPFWindowControl(self.Window)

    def CustomizeWindow(self):
        ''' to be overriden, customize window before launching'''
        pass

    def CreateDataContext(self):
        ''' create DataContext object as ExpandoObject, and bind to ViewModel'''
        self.Window.DataContext = System.Dynamic.ExpandoObject()
        self.DataContext = WPFWindowDataContext(self.Window.DataContext)
        self.DefineDataBinding()

    def DefineDataBinding(self):
        ''' to be overriden, explicitly define individual control data binding targets from xaml
        '''
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
            def delegate(msg):
            # the delegate function to be executed in self.Window Thread
            # since delegate() is defined with context of self.wrapper, it automatically has access to self
            # another option is to use ExpandoObject to pass data -- data itself should be in native .Net type
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