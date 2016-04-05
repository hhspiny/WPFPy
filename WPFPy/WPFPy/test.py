import clr, System
class DotNetINotifyPropertyChanged(System.ComponentModel.INotifyPropertyChanged):
    __namespace__ = "DotNetINotifyPropertyChanged"
    def __init__(self):
        super(DotNetINotifyPropertyChanged, self).__init__()    
    def add_PropertyChanged(self, value):
        pass
    def remove_PropertyChanged(self, value):
        pass
c1=DotNetINotifyPropertyChanged()
c1.add_PropertyChanged("text")
print "C1 success"

class A(DotNetINotifyPropertyChanged):
    __namespace__ = "A"
    def __init__(self):
        super(A,self).__init__()
a1 = A()
a1.add_PropertyChanged("text")
print "a1 success"

