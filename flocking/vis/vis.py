from numpy import *
import pygame
import pygame.locals

class DrawObject(object):
    def __init__(self, r):
        self.r = r
        self.positions = []
    def draw0(self, canvas):
        pass
    def draw1(self, canvas):
        pass
    def draw2(self, canvas):
        pass
    def draw(self, canvas, priority):
        if priority == 0:
            self.positions = canvas.calculate_visible_positions(self.r, 0)
            self.draw0(canvas)
        elif priority == 1:
            self.draw1(canvas)
        elif priority == 2:
            self.draw2(canvas)

class Bird(DrawObject):
    def __init__(self,
                 r,
                 color = (255, 128, 128),
                 light_radius = 1,
                 dark_radius = 2):
        DrawObject.__init__(self, r)
        self.color = color
        self.light_radius = light_radius
        self.dark_radius = dark_radius
    def draw0(self, canvas):
        if self.dark_radius > 0:
            for r in self.positions:
                canvas.draw_circle(r, self.dark_radius * canvas.zoom, color = (self.color[0]/2, self.color[1]/2, self.color[2]/2))
    def draw1(self, canvas):
        if self.light_radius > 0:
            for r in self.positions:
                canvas.draw_circle(r, self.light_radius * canvas.zoom, color = self.color)

class Velocity(DrawObject):
    def __init__(self, r, v,
                 color = lambda x: (255, 255, 255),
                 width = lambda x: 1):
        DrawObject.__init__(self, r)
        self.v = v
        self.norm = linalg.norm(self.v)
        self.color = color(self.norm)
        self.width = width(self.norm)
    def draw2(self, canvas):
        self.length = canvas.velocity_scale(self.norm)
        for r in self.positions:
            canvas.draw_arrow(r, self.v, self.length, color = self.color, width = self.width)

class Force(DrawObject):
    def __init__(self, r, f,
                 color = lambda x: (128, 128, 255),
                 width = lambda x: 1):
        DrawObject.__init__(self, r)
        self.f = f
        self.norm = linalg.norm(self.f)
        self.color = color(self.norm)
        self.width = width(self.norm)
    def draw2(self, canvas):
        self.length = canvas.force_scale(self.norm)
        for r in self.positions:
            canvas.draw_arrow(r, self.f, self.length, color = self.color, width = self.width)

class FlockDrawer(object):
    def __init__(self, flock, flockstep, light_radius = 1, dark_radius = 2):
        self.flock = flock
        self.flockstep = flockstep
        self.light_radius = light_radius
        self.dark_radius = dark_radius
    def draw(self, canvas):
        for i in range(0, self.flock.N):
            if hasattr(self.flock, 'color'):
                c = self.flock.color[i]
            else:
                c = (255, 128, 128)
            canvas.objs.append(
                Bird(self.flock.x[i],
                     color = c,
                     light_radius = self.light_radius,
                     dark_radius = self.dark_radius))
            canvas.objs.append(Velocity(self.flock.x[i], self.flock.v[i]))
            #canvas.objs.append(Force(self.flock.x[i], self.flock.f[i]))
        
class Canvas(object):
    def scr_position(self, r, cell):
        return (r - self.center + cell * self.L) * self.zoom + self.resolution / 2
    def scr_position_visible(self, scr_r):
        return (0 <= scr_r[0] and scr_r[0] < self.resolution[0] and
                0 <= scr_r[1] and scr_r[1] < self.resolution[1])
    def calculate_cells(self):
        max_blocks = array(ceil(self.resolution / self.L / self.zoom), dtype = 'int') + 1
        cells = [array([cx, cy])
                 for cx in range(-max_blocks[0], max_blocks[0]) 
                 for cy in range(-max_blocks[1], max_blocks[1])]        
        self.full_cells = []
        self.partial_cells =  []
        for cell in cells:
            def offset(cell):
                return (- self.center + cell * self.L) * self.zoom + self.resolution / 2
            left_top = self.scr_position(zeros([2]), cell)
            right_bottom = self.scr_position(array([self.L, self.L]), cell)
            if (self.scr_position_visible(left_top) and
                self.scr_position_visible(right_bottom)):
                self.full_cells.append(offset(cell))
            elif self.interval_intersect(
                [left_top[0], right_bottom[0]], 
                [0, self.resolution[0]]) and self.interval_intersect(
                [left_top[1], right_bottom[1]],
                [0, self.resolution[1]]):
                self.partial_cells.append(offset(cell))
    def interval_intersect(self, a, b):
        return not ((a[0] < b[0] and a[1] < b[0]) or
                    (b[1] < a[0] and b[1] < a[1]))
    def calculate_visible_positions(self, r, radius):
        scr_dr = r * self.zoom
        need_check = [cell + scr_dr for cell in self.partial_cells]
        checked = [scr_pos for scr_pos in need_check
                   if self.scr_position_visible(scr_pos)]
        visible = [cell + scr_dr for cell in self.full_cells]
        return visible + checked
    background_color = (0, 0, 0)
    def __init__(self, resolution, center, zoom, L):
        self.clear()
        self.drawers = []
        factor = 10
        self.velocity_scale = lambda norm: factor * norm
        self.force_scale = lambda norm: factor * norm
        self.full_cells = []
        self.partial_cells = []
        self.L = L
        self.center = center
        self.zoom = zoom
        self.resolution = resolution
        self.screen = pygame.display.set_mode(self.resolution)
        self.clock = pygame.time.Clock()
    def draw_circle(self, pos, radius, color):
        pygame.draw.circle(self.screen, color, (int(pos[0]),int(pos[1])), int(radius))
    def draw_arrow(self, pos, direction, norm, color, width):
        if norm != 0:
            dpos = direction / linalg.norm(direction) * norm
            px = double(pos[0])
            py = double(pos[1])
            dx = double(dpos[0])
            dy = double(dpos[1])
            pygame.draw.lines(self.screen, color, False, 
                              [(int(px), int(py)),
                               (int(px + dx), int(py + dy)),
                               (int(px - dy), int(py + dx)),
                               (int(px + dx), int(py + dy)),
                               (int(px + dy), int(py - dx))], width)
    grid_color = (80, 80, 80)
    def draw_grid(self):
        pos = self.calculate_visible_positions(zeros([2]), 0)
        x_set = set([x for (x, y) in pos])
        y_set = set([y for (x, y) in pos])
        for x in x_set:
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.resolution[1]))
        for y in y_set:
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.resolution[0], y))
    def draw(self):
        self.screen.fill(self.background_color)
        self.draw_grid()
        self.clear()
        self.calculate_cells()
        [drawer.draw(self) for drawer in self.drawers]
        for priority in [0, 1, 2]:
            for obj in self.objs:
                obj.draw(self, priority)
        pygame.display.flip()
    def clear(self):
        self.objs = []
    def treat_keyboard(self):
        for event in pygame.event.get():
            pass
        keystate = pygame.key.get_pressed()
        if keystate[pygame.locals.K_KP_PLUS]:
            self.zoom *= 1.1
        if keystate[pygame.locals.K_KP_MINUS]:
            self.zoom /= 1.1
        if keystate[pygame.locals.K_KP2]:
            self.center += array([0, self.resolution[1]/self.zoom/30])
        if keystate[pygame.locals.K_KP8]:
            self.center -= array([0, self.resolution[1]/self.zoom/30])
        if keystate[pygame.locals.K_KP4]:
            self.center -= array([self.resolution[0]/self.zoom/30, 0])
        if keystate[pygame.locals.K_KP6]:
            self.center += array([self.resolution[0]/self.zoom/30, 0])
        self.center = fmod(self.center, self.L)
