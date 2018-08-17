# gglogic boolean logic device simulations for ggmath

from ggmath import MathApp, _MathDynamic
from abc import ABCMeta, abstractmethod


# decorator for _getvalue or any value handler that may experience recursion
def recursiontrap(handler):
    def trapmagic(self):
        if not self.ingetvalue:
            self.ingetvalue = True
            self.lastget = handler(self)
            self.ingetvalue = False
            return self.lastget
        else:
            self.ingetvalue = False
            return self.lastget
            
    return trapmagic 


class _BoolDevice(_MathDynamic, metaclass=ABCMeta):

    def __init__(self, mininputqty, *args, **kwargs):
        """
        Required Inputs
        
        * **mininputqty** minimum number of inputs possible
        
        Optional keyword arguments
        
        * **namedinputs** list of input names
        """
        self.In = [None]*mininputqty
        self.Enable = True
        namedinputs = kwargs.get('namedinputs', [])
        self._indict = {name:self.Eval(None) for name in namedinputs}
        self.ingetvalue = False
        self.lastget = None
        

    @property
    def In(self):
        return self._input
    
    @In.setter
    def In(self, val):
        try:
            self._input = [self.Eval(v) for v in list(val)]
        except TypeError:
            self._input = [self.Eval(val)]
            
    # Enable attribute controls the "tri-state" of output
    @property
    def Enable(self):
        return self._enable
    
    @Enable.setter
    def Enable(self, val):
        self._enable = self.Eval(val)
        
    @abstractmethod
    @recursiontrap     # MUST use with any implementation that may recurse!
    def _getvalue(self):
        return None
    
    def _inputState(self, value):
        """
        interprets a value that could be single input or a list of inputs!
        """
        try:
            inputs = [].extend(value)
        except TypeError:
            inputs = [value]
        scalars = [v() for v in inputs]
        ones = scalars.count(True) + scalars.count(1)
        zeros = scalars.count(False) + scalars.count(0)
        if ones > 0 and zeros > 0:
            raise ValueError("Conflicting inputs found")
        if ones > 0:
            return True
        elif zeros > 0:
            return False
        else: 
            return None
    
    def __call__(self):
        if self.Enable:
            return self._getvalue()
        else:
            return None
    
    def GetInput(self, inputname):
        return self._inputState(self._indict[inputname])

    def SetInput(self, inputname, reference):
        self._indict[inputname] = self.Eval(reference)
    


class _BoolOneInput(_BoolDevice):

    def __init__(self, *args, **kwargs):
        """ 
        No Required Inputs
        """
        super().__init__(1, *args, **kwargs)

    
class _BoolMultiInput(_BoolDevice):

    def __init__(self, *args, **kwargs):
        """ 
        No Required Inputs
        """
        super().__init__(2, *args, **kwargs)


class BoolNOT(_BoolOneInput):

    @recursiontrap
    def _getvalue(self):
        inval = self._inputState(self.In[0])
        if inval == None:
            return True  # equivalent to an "open" input
        else:
            return not inval


class BoolAND(_BoolMultiInput):
    
    @recursiontrap
    def _getvalue(self):
        for v in self._input:
            if not self._inputState(v):
                return False
        return True
        
class BoolNOR(_BoolMultiInput):
    
    @recursiontrap
    def _getvalue(self):
        for v in self._input:
            if self._inputState(v):
                return False
        return True
        
class BoolNAND(_BoolMultiInput):
    
    @recursiontrap
    def _getvalue(self):
        for v in self._input:
            if not self._inputState(v):
                return True
        return False
        
class BoolSRFF(_BoolOneInput):
    
    def __init__(self, *args, **kwargs):
        """
        SR Flip Flop
        
        Optional keyword arguments
        
        * **gateclass** one of BoolNAND or BoolNOR (default)
        """
        kwargs['namedinputs'] = ['R','S']
        super().__init__(*args, **kwargs)
        gate = kwargs.get('gateclass', BoolNOR)
        self.IC1 = gate()
        self.IC2 = gate()

    # we can only assign IC1 and IC2 inputs when this device's inputs are set
    def SetInput(self, inputname, reference):
        super().SetInput(inputname, reference)
        if inputname == 'R':
            self.IC1.In = reference, self.IC2
        elif inputname == 'S':
            self.IC2.In = reference, self.IC1

        
    def _getvalue(self):
        return self.IC1()
        
    def Q_(self):
        return self.IC2()
        
    def Q(self):
        return self._getvalue()
        

class BoolJKFF(_BoolOneInput):
    
    def __init__(self, *args, **kwargs):
        """
        JK Flip Flop
        
        Optional keyword arguments
        
        """
        self.InputNames = ['J','K','CLK']
        kwargs['namedinputs'] = self.InputNames
        super().__init__(*args, **kwargs)
        self.IC1 = BoolNAND()
        self.IC2 = BoolNAND()
        self.ICJ = BoolNAND()
        self.ICK = BoolNAND()
        self.IC1.In = self.ICJ, self.IC2
        self.IC2.In = self.ICK, self.IC1
    # we can only assign ICJ, ICK inputs when this device's inputs are set
    def SetInput(self, inputname, reference):
        super().SetInput(inputname, reference)
        for i in self.InputNames:
            if self._indict[i]() is None:
                return
        print(self.IC2, self._indict['J'],  self._indict['K'], self._indict['CLK'])    
        #self.ICJ.In = self.IC2, self._indict['J'], self._indict['CLK']
        #self.ICK.In = self.IC1, self._indict['K'], self._indict['CLK']
        
    def _getvalue(self):
        return self.IC1()
        
    def Q_(self):
        return self.IC2()
        
    def Q(self):
        return self._getvalue()

class TestDevice(_BoolOneInput):
    
    def __init__(self, *args, **kwargs):
        kwargs['namedinputs'] = ['in1', 'in2']
        super().__init__(*args, **kwargs)
        
    def out1(self):
        return self.GetInput('in1') and self.GetInput('in2')
        
    def out2(self):
        return self.GetInput('in1') or self.GetInput('in2')
        
    def _getvalue(self):
        return None
        
        
        

    

# test code here
if __name__ == "__main__":
    
    from ggmath import GlassButton, LEDIndicator, MetalToggle
    

    """
    IC1 = BoolNOT()
    IC2 = BoolAND()
    
    b1 = MetalToggle(1, (1,0))
    b2 = MetalToggle(1, (1,0.3))
    db1 = LEDIndicator((1.3,0), b1)
    db2 = LEDIndicator((1.3,0.3), b2)

    b3 = MetalToggle(1, (1,0.6))
    b4 = MetalToggle(1, (1,0.9))
    db1 = LEDIndicator((1.3,0.6), b3)
    db2 = LEDIndicator((1.3,0.9), b4)


    d2 = LEDIndicator((1.5,0.45), IC2)
    
    IC2.In = b1, b2
    IC2.In = IC2.In + [b3, b4]
    
    button = GlassButton(None, (0,0))
    LED = LEDIndicator((0,-1), IC1)
    IC1.In = button 


    t1 = MetalToggle(1, (1,-1))
    t2 = MetalToggle(1, (1, -1.3))
    td = TestDevice()
    dt1 = LEDIndicator((1.3, -1), t1)
    dt2 = LEDIndicator((1.3, -1.3), t2)
    dtd1 = LEDIndicator((1.5, -1), td.out1)
    dtd2 = LEDIndicator((1.5, -1.3), td.out2)
    td.SetInput('in1', t1)
    td.SetInput('in2', t2)
    """
    
    """ SR Flip Flop demo
    IC1 = BoolSRFF(gateclass=BoolNAND)
    Inv1 = BoolNOT()
    Inv2 = BoolNOT()

    b1 = GlassButton(None, (0,0))
    b2 = GlassButton(None, (0,-0.5))
    Inv1.In = b1
    Inv2.In = b2
    
    IC1.SetInput('R', Inv1)
    IC1.SetInput('S', Inv2)

    d1 = LEDIndicator((0.5,0), IC1)
    d2 = LEDIndicator((0.5,-0.5), IC1.Q_)
    """

    """ JK Flip Flop demo
    """
    
    IC1 = BoolJKFF()
    t1 = MetalToggle(0, (0,0.5))
    b1 = GlassButton(None, (0,0))
    t2 = MetalToggle(0, (0,-0.5))

    IC1.SetInput('J', t1)
    IC1.SetInput('K', t2)
    IC1.SetInput('CLK', b1)

    d1 = LEDIndicator((0.5,0.5), IC1)
    d2 = LEDIndicator((0.5,-0.5), IC1.Q_)
    """
    """
    
    app = MathApp()
    app.run()