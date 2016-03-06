# define base class framework for Python.Net interface with WPF

import clr, System
clr.AddReference(r"wpf\PresentationFramework")
from System import IO, Windows, Threading, ComponentModel
from System import TimeSpan


class WPFWindowControl(System.Object):
    ''' surrogate for Window.Control object to provide direct access to it
    '''
    def __init__(self, window):
        self._Window = window

    def __getattr__(self, name):
        control = self._Window.FindName(name)
        if control == None:
            raise AttributeError("%s window does not have %s control" % (self._Window.Title, name))
        else:
            return control
 
class DotNetExpandoObject(System.Dynamic.ExpandoObject):
    ''' Wrapper for ExpandoObject to allow pythonic access
        ExpandoObject implements INotifyPropertyChanged for its properties
    '''
    def __init__(self):
        super(DotNetExpandoObject,self).__init__()

    def __getattr__(self,name):
            obj = None
            wrapped = System.Collections.Generic.IDictionary[System.String, System.Object](self)
            ret = wrapped.TryGetValue(name, obj)
            if ret[0]:
                return ret[1]
            else:
                raise AttributeError, "%s has no attribute '%s'" % ("WPFExpandoObject", name)
 
    def __setattr__(self,name,obj):
        # DataContext's attribute
            wrapped = System.Collections.Generic.IDictionary[System.String, System.Object](self)
            if wrapped.ContainsKey(name):
                wrapped.set_Item(name, obj)
            else:
                wrapped.Add(name, obj)

class WPFWindow(System.Object):
    """
    Wrapper class for Systems.Window.Window class. 
    1. Create and save WPF/XAML window in self.Window, and launch in a separate thread
    2. All methods that could access self.Window object should be defined with decorator @WPFWindow.WPFWindowThread
        to ensure thread safe
    3. Bind Window.DataContext to class derived from ExpandoObject (implements INotifyPropertyChanged)
    4. self.Window contains the WPF window object, but self.Controls acts as surrogate for access controls directly
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
        ''' To bind Window.DataContext to ExpandoObject, and have access to the obj via self.DataContext
        '''
        self.DataContext = DotNetExpandoObject()
        self.Window.DataContext = self.DataContext
        self.InitDataBinding()
        # register eventhandler for DataContext changed event -- after all data binding are initialized
        System.ComponentModel.INotifyPropertyChanged(self.DataContext).PropertyChanged += self.DataContextChanged


    def InitDataBinding(self):
        ''' to be overriden, explicitly define individual control data binding targets from xaml
            recommend to explicit binding to initialize
        '''
        pass
    
    def DataContextChanged(self,s,e):
        ''' Window.DataContext property changed event, to be overriden
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