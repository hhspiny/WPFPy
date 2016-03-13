# define base class framework for Python.Net interface with WPF
# convention:  
#   .Net Attributes/Method starts with capital letter
#   Python attributes/methods follow conventional way of first letter lower case

import clr, System
clr.AddReference(r"wpf\PresentationFramework")

class WindowControlSurrogate(System.Object):
    ''' surrogate for Window.Control object to provide direct access
    '''
    def __init__(self, window):
        self._window = window

    def __getattr__(self, name):
        control = self._window.FindName(name)
        if control == None:
            raise AttributeError("%s window does not have %s control" % (self._window.Title, name))
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
                raise AttributeError, "%s has no attribute '%s'" % ("DotNetExpandoObject", name)
 
    def __setattr__(self,name,obj):
        # DataContext's attribute
            wrapped = System.Collections.Generic.IDictionary[System.String, System.Object](self)
            if wrapped.ContainsKey(name):
                wrapped.set_Item(name, obj)
            else:
                wrapped.Add(name, obj)

class Window(System.Object):
    """
    Wrapper class for Systems.Window.Window class. 
    1. Create WPF/XAML window in self.window, and launch in a separate thread. provide self.controls to access controls
    2. Provide decorator @WPFWindow.WPFWindowThread for thread aware direct access to self.window object
    3. Bind self.window.DataContext a surrogate class derived from ExpandoObject
    """
    
    def __init__(self, xamlFile,
                ownThread = False, attachThread = False,
                show=True ,modal = False, 
                viewModel = None 
                 ):
        """ xamlFile:       xamlFile to create Window object
            viewModel:      provide view model object
            ownThread:      create a separate thread for this window
            attachThread:   attach to the created window thread
            show:           show the window during construction
            modal:          block input of other windows (in the same thread)
        """
        self.xamlFile=xamlFile
        self.VM = viewModel
        self.ownThread = ownThread
        self.attachThread = attachThread
        self.modal = modal
        self.showWindow = show
        # events defined in Xaml file
        self.eventTable = {}

        if self.ownThread:
            self.createThread()
        else:
            self._initialize()
   
    def _initialize(self):
        ''' initialize window by creating window object from xaml file and call rest init methods '''
        try:
            inStream = System.IO.StreamReader(self.xamlFile)
            xdoc = System.Xml.Linq.XDocument.Load(inStream)
            self.processXaml(xdoc)
            outStream = System.IO.MemoryStream()
            xdoc.Save(outStream)
            outStream.Seek(0,System.IO.SeekOrigin.Begin)
            self.window = System.Windows.Markup.XamlReader.Load(outStream)
            outStream.Close()
            self.controls = WindowControlSurrogate(self.window)
            self.window.Closed += self.windowClosed
        except System.Windows.Markup.XamlParseException as e:
        # need to test what exception gets thrown and print information
            print "Error parsing %s. Error %s" % (self.xamlFile, e.ToString())
            raise

        if self.showWindow: 
            if self.modal:
                self.window.ShowDialog()
            else:
                self.window.Show()
        self.initWindow()
        self.createEventMapping()
        self.createDataContext()

    def windowClosed(self,s,e):
        # window closed event, default to invoke thread shutdown
        self.customWindowClosed(s,e)
        System.Windows.Threading.Dispatcher.CurrentDispatcher.BeginInvokeShutdown(System.Windows.Threading.DispatcherPriority.Background)

    def processXaml(self, xdoc):
        ''' customized Xaml for dynamic loading. also build control event table
        '''
        for elem in xdoc.Descendants():
            # find out the events and build event handling table
            name = None
            for attr in elem.Attributes():
                if "{http://schemas.microsoft.com/winfx/2006/xaml}Name" in attr.Name.ToString():
                    name = str(attr.Value)
            if name == None:
                continue
            self.eventTable[name] = []
            for attr in elem.Attributes():
            # identify event by name pattern "name_event"
                tmpStr = name+"_"+attr.Name.ToString()
                if tmpStr in attr.Value:
                        self.eventTable[name].append([attr.Name, attr.Value])          
            for item in self.eventTable[name]:
                elem.Attribute(item[0]).Remove()
            if len(self.eventTable[name]) == 0:
                self.eventTable.pop(name)        
        return

    def createDataContext(self):
        ''' To bind Window.DataContext to ExpandoObject, and have access to the obj via self.DataContext
        '''
        self.dataContext = DotNetExpandoObject()
        self.window.DataContext = self.dataContext
        self.initDataBinding()
        # register eventhandler for DataContext changed event -- after all data binding are initialized
        System.ComponentModel.INotifyPropertyChanged(self.dataContext).PropertyChanged += self.dataContextChanged


    def createEventMapping(self):
        ''' To auto map control events to method
        '''
        for key in self.eventTable.keys():
            control = self.window.FindName(key)
            for item in self.eventTable[key]:
                event = item[0]
                method = item[1]
                eventObj = getattr(control,event.ToString())
                try:
                    methodObj = getattr(self, method)
                    eventObj += methodObj
                except AttributeError:
                # allows a event handler defined in Xaml to be absent
                    pass
        self.initEventMapping()

#  === below are abstract method to be overriden in derived class to provide customized function === #        
    def initWindow(self):
        ''' to be overriden, initialize window before launching'''
        pass

    def initDataBinding(self):
        ''' to be overriden, initialize data binding and set initial values
        '''
        pass

    def initEventMapping(self):
        ''' to be overriden, explicitly define event handler mapping
        '''
        pass
    
    def dataContextChanged(self,s,e):
        ''' to be overriden, Window.DataContext property changed event process. need to be called last during window construction
            identify the property changed by e.PropertyName
        '''
        pass
        
    def customWindowClosed(self,s,e):
        ''' to be overriden, customized window close event handler -- before thread shutdown 
        '''
        pass

# the following methods handle when the window requires its own thread 
    def createThread(self):
        ''' create a separate thread for the window during construction '''
        self.__evt = System.Threading.AutoResetEvent(False)
        self.thread = System.Threading.Thread(System.Threading.ThreadStart(self.threadStart))
        self.thread.IsBackground = True
        self.thread.SetApartmentState(System.Threading.ApartmentState.STA)
        self.thread.Start()
        # wait for window creation before continue
        self.__evt.WaitOne() 
        # block calling thread or not
        if self.attachThread:
           self.thread.Join()
        return self.thread

    def threadStart(self):
        ''' start the thread to intialize window'''

        # check if current thread has a sync_context, if not create one        
        self.syncContext = System.Threading.SynchronizationContext.Current
        if self.syncContext == None:
            self.syncContext =  System.Windows.Threading.DispatcherSynchronizationContext(System.Windows.Threading.Dispatcher.CurrentDispatcher)
            System.Threading.SynchronizationContext.SetSynchronizationContext(self.syncContext)    
        # add window close measurement  
        self._initialize()
        self.__evt.Set()

        if System.Windows.Application.Current == None:
        # if there is application yet, create one, and launch the current window as MainWindow
            app = System.Windows.Application()
            app.ShutdownMode = System.Windows.ShutdownMode.OnMainWindowClose
            app.Run(self.window)
        else:
        # if there is already an application, then just run the window
            System.Windows.Threading.Dispatcher.Run() 
         
    # Any functions that could access self.window should have the WPFWindowThread decorator to pass msg between threads
    # The function can be a class method or a global method, as long as it has first arg is a WPFWindow object
    @staticmethod
    def windowThread(func):
        ''' decorator to wrapper calls referencing self.Windo in thread safe call, the function itself should have WPFWindow object as first arg '''
        def wrapper(self, *args, **kwargs):
        # wrapper function to run within correct thread context of WPFWindow object (farg)
            def delegate(msg):
            # the delegate function to be executed in self.window Thread
            # since delegate() is defined with context of self.wrapper, it automatically has access to self
            # another option is to use ExpandoObject to pass data -- data itself should be in native .Net type
                retval = func(self, *(self._msg[0]),**(self._msg[1]))
                self._msg[2] = retval
            
            # use self._msg to pass on parameters to delegate function
            self._msg = [args, kwargs, None]
            
            if System.Threading.SynchronizationContext.Current == self.syncContext:
            #   executing in WPFWindow's context
                delegate(None)
                retval =  self._msg[2]
                return retval
            else:
            #  send delegate function to proper context
                self.syncContext.Send( System.Threading.SendOrPostCallback(delegate), None)
                retval =  self._msg[2]
                return retval
        return wrapper      