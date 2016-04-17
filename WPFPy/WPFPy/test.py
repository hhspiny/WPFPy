import clr, System
class DotNetINotifyPropertyChanged(System.ComponentModel.INotifyPropertyChanged):
#class DotNetINotifyPropertyChanged(System.Object):
    __namespace__ = "DotNetINotifyPropertyChanged"
    def __init__(self):
        super(DotNetINotifyPropertyChanged, self).__init__()    
    def add_PropertyChanged(self, value):
        pass
    def remove_PropertyChanged(self, value):
        pass
#c1=DotNetINotifyPropertyChanged()
#print c1.add_PropertyChanged
#print dir(c1.add_PropertyChanged)
#print c1.add_PropertyChanged.im_func
#c1.add_PropertyChanged("text")
#print "C1 success"

class A(DotNetINotifyPropertyChanged):
    __namespace__ = "A"
    def __init__(self):
        super(A,self).__init__()
#a1 = A()
#print a1.add_PropertyChanged
#print dir(a1.add_PropertyChanged)
#a1.add_PropertyChanged("text")
#print "a1 success"

class baseA(System.Object):
#    __namespace__ = "A"
    def __init__(self):
        pass
    def methodA(self):
        print "A"
class baseB(baseA):
#    __namespace__ = "B"
    def __init__(self):
        super(baseB,self).__init__()
    def methodB(self):
        print "B"

class baseNA(System.Random):
    __namespace__ = "System"
    def __init__(self):
        super(baseNA,self).__init__()
#    @clr.clrmethod(System.String,[])
    def ToString(self):
        return "string"

class baseNB(baseNA):
    __namespace__ = "System"
    def __init__(self):
        super(baseNB,self).__init__()

def testInherit():
    bna = baseNA()
    print bna.ToString()
    print bna._Random__ToString()
    bnb = baseNB()
    print bnb.ToString()
    print bnb._baseNA__ToString()
    print bnb._Random__ToString()

class testAttr(System.Object):
    def __init__(self):
        super(testAttr,self).__init__()
#    def __getattr__(self,name):
#        print "__getattr__"
    def __setattr__(self,name,value):
        print "__setattr__"
        super(testAttr,self).__setattr__(name,value)