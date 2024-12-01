import math, pygame, sys
pygame.init()

import threading

vec2 = pygame.math.Vector2
Pallete = [(30,33,43), (0, 155, 114), (164, 48, 63), (230, 250, 252)]

RES = vec2(1280, 720)
screen = pygame.Window("Sine Visualzier", RES)
screen.always_on_top = True

def clamp(val, mini, maxi):
    if val >= maxi:
        return maxi
    if val <= mini:
        return mini
    return val


### timer
class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.finsied = False
    
    def update(self, deltaTime):
        self.timer += deltaTime
        if self.timer >= self.duration:
            self.finsied = True

    def getPercent(self):
        return clamp(self.timer/self.duration, 0, 1)*100

    def getNormalized(self):
        return clamp(self.timer/self.duration, 0, 1)

    def isFinished(self):
        return self.finsied
    
    def end(self):
        self.timer = 0
        self.finsied = True

    def reset(self):
        self.timer = 0
        self.finsied = False

class Interpolate:
    @staticmethod
    def lerp(final, initial, time, duration):
        return initial + (final-initial)*clamp(time/duration, 0, 1)
    
    @staticmethod
    def lerpNorm(final, initial, time):
        return initial + (final-initial)*clamp(time, 0, 1)

    @staticmethod
    def easeInOutNorm(final, initial, time):
        # Ease-in-out function
        if time < 0.5:
            # Ease-in phase
            value = initial + (final - initial) * (2 * time * time)
        else:
            # Ease-out phase
            value = initial + (final - initial) * (1 - pow(-2 * time + 2, 2) / 2)
        
        return value

### sine visualizer
class SineVisualizer:
    class SineWave:
        def __init__(self, a, w, k=0):
            ### a -- ampliture
            ### w = frequency
            ### k = shift

            self.amplitude = a 
            self.freq = w 
            self.shift = k

        def getValue(self, x):
            #### x- radian
            return self.amplitude*math.sin(self.freq*x + self.shift)
        

    def __init__(self, res):
        self.resolution = res
        self.PI = 3.14
        self.baseLineDrawn = False
        self.baseLineTimer = Timer(2)

        self.baseLine = {"width":3, "color":Pallete[3], "y":self.resolution.y//2}

        self.sineWaves = []
        self.sineWaves.append(self.SineWave(100, 1, 0))
        # self.sineWaves.append(self.SineWave(100, 2, 0))

        self.time = 0
        self.speed = 5

        self.scale = 10
        self.drawStepSize= 5

        self.fill = True
        self.outline = True

        self.absolute = False

    def addSineWave(self, a, w, k):
        self.sineWaves.append(self.SineWave(a, w, k))

    def setFill(self, val):
        self.fill = bool(val)

    def setOutline(self, val):
        self.outline = bool(val)

    def setSpeed(self, timeSpeed):
        self.speed = timeSpeed

    def setScale(self, scale):
        self.scale = scale

    def update(self, dt):
        ### updare time
        self.mousePos = pygame.mouse.get_pos()

        if not self.baseLineDrawn:
            self.baseLineTimer.update(dt)
            if self.baseLineTimer.isFinished():
                self.baseLineDrawn = True

        ### updating sine waves
        self.time += dt*self.speed

        for wave in self.sineWaves:
            wave.shift = self.time

    def getSineValue(self, x):

        y = self.baseLine['y']
        for wave in self.sineWaves:
            y += wave.getValue((x/self.resolution.x)*self.PI*self.scale)

        return y


    def draw(self, window):
        if not self.baseLineDrawn:
            width = Interpolate.easeInOutNorm(self.resolution.x, 0, self.baseLineTimer.getNormalized())
            pygame.draw.line(window, self.baseLine['color'], (0, self.baseLine['y']), (width, self.baseLine['y']), self.baseLine['width'])

            for x in range(0, int(Interpolate.easeInOutNorm(self.resolution.x, 0, self.baseLineTimer.getNormalized())), self.drawStepSize):

                y = self.baseLine['y']
                yPrev = self.baseLine['y']
                for wave in self.sineWaves:
                    if not self.absolute:
                        y += wave.getValue((x/self.resolution.x)*self.PI*self.scale)
                        yPrev += wave.getValue(((x-self.drawStepSize)/self.resolution.x)*self.PI*self.scale)
                    else:
                        y += abs(wave.getValue((x/self.resolution.x)*self.PI*self.scale))
                        yPrev += abs(wave.getValue(((x-self.drawStepSize)/self.resolution.x)*self.PI*self.scale))

                if self.fill:
                    pygame.draw.line(window, Pallete[2], (x, self.baseLine['y']), (x, y), 1)

                if self.outline:
                    pygame.draw.line(window, Pallete[3], (x-self.drawStepSize, yPrev), (x, y), 1)

                if self.mousePos[0] <= width:
                    pygame.draw.circle(window, Pallete[3], (self.mousePos[0], self.getSineValue(self.mousePos[0])), 5)

        else:
            pygame.draw.line(window, self.baseLine['color'], (0, self.baseLine['y']), (self.resolution.x, self.baseLine['y']), self.baseLine['width'])

            for x in range(0, int(self.resolution.x), self.drawStepSize):

                y = self.baseLine['y']
                yPrev = self.baseLine['y']
                for wave in self.sineWaves:
                    if not self.absolute:
                        y += wave.getValue((x/self.resolution.x)*self.PI*self.scale)
                        yPrev += wave.getValue(((x-self.drawStepSize)/self.resolution.x)*self.PI*self.scale)
                    else:
                        y += abs(wave.getValue((x/self.resolution.x)*self.PI*self.scale))
                        yPrev += abs(wave.getValue(((x-self.drawStepSize)/self.resolution.x)*self.PI*self.scale))

                if self.fill:
                    pygame.draw.line(window, Pallete[2], (x, self.baseLine['y']), (x, y), 1)

                if self.outline:
                    pygame.draw.line(window, Pallete[3], (x-self.drawStepSize, yPrev), (x, y), 1)
                
                pygame.draw.circle(window, Pallete[3], (self.mousePos[0], self.getSineValue(self.mousePos[0])), 5)


class TerminalHandler:
    ### requires threading module
    def __init__(self):
        self.thread = threading.Thread(target=self.handle, daemon=True)

        ### can be altered
        self.prompt = "Command> "
        self.exitCode = "Q"
        self.prefix = "[SYSTEM]"
        

    def begin(self):
        self.thread.start()

    def customHandle(self, text):
        #### can be empty 
        global sine
        
        if "add wave" in text: 
            val = text.split(" ")[2:]
            try:
                ampl = float(val[0])
                w = float(val[1])
                k = float(val[2])

                sine.addSineWave(ampl, w, k)
            except:
                print(self.prefix, "Not enough parameters: add wave amplitude, freq, shift")
            
        if "set scale" in text:
            val = text.split(" ")[2:]
            sine.setScale(float(val[0]))

        if "set speed" in text:
            val = text.split(" ")[2:]
            sine.setSpeed(float(val[0]))

        if "set outline" in text:
            val = text.split(" ")[2:]
            if val[0].lower() == "true":
                sine.setOutline(True)
            if val[0].lower() == "false":
                sine.setOutline(False)
            
        if "set fill" in text:
            val = text.split(" ")[2:]
            if val[0].lower() == "true":
                sine.setFill(True)
            if val[0].lower() == "false":
                sine.setFill(False)
                
        if "quit" in text:
            pygame.quit()
            sys.exit()

    def handle(self):
        print(self.prefix, "Command terminal initiated!")
        while 1:
            userInput = str(input(self.prompt))
            self.customHandle(userInput)
            # print(self.prefix, "Unknown command.\n\n")

### local gameloop variaqbles
sine = SineVisualizer(RES)
terminal = TerminalHandler()
terminal.begin()
dt = 1/120
clock = pygame.time.Clock()
FPS = 12000

#### displaing fonts
mousePosFont = pygame.font.Font("font.ttf", 20)

#@### gameloop
while 1:
    window = screen.get_surface()
    clock.tick(FPS)

    dt = 1/clock.get_fps() if clock.get_fps() else 1/60
    window.fill(Pallete[0])
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.MOUSEWHEEL:
            sine.setScale(sine.scale - event.y*0.5)

    pos = pygame.mouse.get_pos()
    mousePos = mousePosFont.render(f"Mouse: {int(pos[0])} x {int(pos[1])}", False, Pallete[3], None)
    mousePosRect = mousePos.get_rect(topleft=(10, 684))

    fps = mousePosFont.render(f"Fps: {int(clock.get_fps())}", False, Pallete[3], None)
    fpsRect = fps.get_rect(center=(1220, 684))

    #### updatuig
    sine.update(dt)

    sine.draw(window)

    #### to improve visuales
    pygame.draw.rect(window, Pallete[1], (0,0,RES.x ,RES.y), 4, 5)

    window.blit(mousePos, mousePosRect)
    window.blit(fps, fpsRect)


    screen.flip()