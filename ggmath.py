# ggmath - ggame extensions for geometry and mathematics in the browser

from ggame import Color, LineStyle, LineAsset, Sprite, App

ls = LineStyle(3, Color(0x000000, 1))
la = LineAsset(100, 100, ls)
#sp = Sprite(la, (100,100))

class LineSegment(Sprite):
    ls = LineStyle(1, Color(0x000000, 1))
    la = LineAsset(0,0, LineSegment.ls)
    
    def __init__(self, start, end, style=LineStyle(1, Color(0,1))):
        self._start = start
        self._end = end
        self._style = style
        super().__init__(LineSegment.la, start)
        self._newSegment(self._start, self._end, self._style)
        
    def _newSegment(self, start, end, style):
        self.GFX.destroy()
        self.asset = LineAsset(end[0]-start[0], end[1]-start[1], style)
        self.GFX = self.asset.GFX
        self.GFX.visible = True        
    
        
    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, val):
        self._start = val
        self._newSegment(self._start, self._end, self._style)

        
    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, val):
        self._end = val
        self.la = LineAsset(end[0]-start[0], end[1]-start[1], style)
        
    def step(self):
        self.start = (self.start[0]+1, self.start[1])
        
        
l = LineSegment((100,100), (200,200))

class MathApp(App):
    
    def step(self):
        for spr in MathApp.getSpritesbyClass(LineSegment):
            pass
            #spr.step()

ap = MathApp()
ap.run()