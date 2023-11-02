import pygame,sys,os,time
from pygame.locals import *
pygame.init()

class Tools:
    def __init__(self,canvas):
        self.canvas = canvas
    
    def existing_tile(self,coords):
        for tile, check_coords in self.canvas.TILES:
            if check_coords == coords:
                return True
            
        return False

    def place_tile(self,coords):
        tile = self.canvas.tile_selected
        if not self.existing_tile(coords):
            self.canvas.TILES.append([tile,coords])


class Utils:

    ROOT_PATH = './data'
    IMAGES = dict()

    @classmethod
    def load_images(cls):
        for folder in os.listdir(cls.ROOT_PATH + '/images'):
            image_list = list()
            for image in os.listdir(cls.ROOT_PATH + '/images/' + folder):
                data_image = pygame.image.load(cls.ROOT_PATH + '/images/' + folder + '/' + image).convert()
                data_image.set_colorkey((0,0,0))
                image_list.append(data_image)
            cls.IMAGES[folder] = image_list
        
        return cls.IMAGES


class Canvas:
    def __init__(self, tile_scale=16, layers=10):

        pygame.display.set_caption('LEVEL EDITOR V6')
        self.FPS = pygame.time.Clock()
        self.last_time = time.time()
        
        self.SCREEN = pygame.display.set_mode((1000,800))
        self.SIDEBAR = pygame.Surface((200,800))
        self.LAYERS = [pygame.Surface((800,800)) for _ in range(layers)]
        self.TILES = list()

        self.TILE_SCALE = tile_scale
        self.FONT_PATH = './data/font/Minecraft.ttf'
        self.asset_selected = {'asset':None, 'rect':None, 'id':None}
        self.tile_selected = {'tile': None, 'rect':None, 'id':None}
        
        self.ASSETS = Utils.load_images()
        self.tools = Tools(self)
        self.divider = 0

        self.mouse = None
        self.clicking = None
        self.keypressed = True
        self.current_tool = 1
        self.current_layer = 1
    
    def labels(self,surface=None,font_size=20,text=None,color=(255,255,255),location=(0,0)):
        font = pygame.font.Font(self.FONT_PATH,font_size)
        label = font.render(text,False,color)
    
        return surface.blit(label,location)

    def frame_delta_time(self,fps=60):
        delta_time = time.time() - self.last_time
        delta_time += fps
        self.last_time = time.time()

        return delta_time


    def button_event(self, buttons=list()):
        for button in buttons:
            if self.clicking and button['rect'].collidepoint(self.clicking):
                return button
            
            
    def assets_selection(self, surface=None):
        gap = 0
        buttons = list()
        for indx, folder in enumerate(os.listdir(Utils.ROOT_PATH + '/images')):
            gap += 1
            if self.asset_selected['id']  == indx:
                button_rect = self.labels(surface=surface,text=folder,font_size=15,location=(15,(indx * 25) + 10),color=(128,128,128))
            else:
                button_rect = self.labels(surface=surface,text=folder,font_size=15,location=(15,(indx * 25) + 10))
            buttons.append({'asset':folder, 'rect':button_rect, 'id': indx})

        self.divider = int(gap*30)

        pygame.draw.line(surface, 'white', (0,self.divider), (200,self.divider),2)


        if self.button_event(buttons=buttons) != None:
            self.asset_selected = self.button_event(buttons=buttons)

    def tiles_selection(self, surface=None):
        render_condition = ['foliage','decoration']
        buttons = list()
        resize = 32
        if self.asset_selected['asset'] != None:
            for indx, image in enumerate(self.ASSETS[self.asset_selected['asset']]):
                render_image = image.copy()
                if self.asset_selected['asset'] in render_condition:
                    resize = 64
                render_image = pygame.transform.scale(image,(resize,resize))
                y_offset = indx * (resize + 20)
                button_rect = surface.blit(render_image,(15, y_offset + self.divider + 20))
                buttons.append({'tile':image, 'rect':button_rect, 'id': indx})


        if self.button_event(buttons=buttons) != None:
            self.tile_selected = self.button_event(buttons=buttons)
            pygame.draw.rect(surface, (0,255,0), self.tile_selected['rect'], 2)


    def map_redering(self):
        for tile, coords in self.TILES:
            self.LAYERS[tile['layer']].blit(tile['tile'],coords)


    def run(self):
        while 1:
            delta_time = self.frame_delta_time(fps=100)

            self.SCREEN.fill((25,25,25))
            for layer in self.LAYERS:
                layer.set_colorkey((0,0,0))
            self.SIDEBAR.fill((45,45,45))
        

            self.mouse = pygame.mouse.get_pos()
            x_grid = int(self.mouse[0]-200)//self.TILE_SCALE
            y_grid = int(self.mouse[1])//self.TILE_SCALE


            if x_grid >= 0: 
                grid_mouse = (x_grid,y_grid)
            else:
                grid_mouse = (0,0)
            
            self.assets_selection(self.SIDEBAR)
            self.tiles_selection(self.SIDEBAR)

            if self.clicking and self.clicking[0] > 200:
                self.tile_selected['layer'] = len(self.LAYERS) - self.current_layer
                match self.current_tool:
                    case 1:
                        coords = (grid_mouse[0]*self.TILE_SCALE,grid_mouse[1]*self.TILE_SCALE)
                        self.tools.place_tile(coords)


            self.map_redering()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = self.mouse
                if event.type == pygame.MOUSEBUTTONUP:
                    self.clicking = None

                if event.type == pygame.KEYDOWN and self.keypressed:
                    if event.key == pygame.K_q:
                        if self.current_layer >= len(self.LAYERS):    
                            self.current_layer = 0
                        self.current_layer += 1

                    if event.key == pygame.K_e:
                        if self.current_layer <= 1:    
                            self.current_layer = 11
                        self.current_layer -= 1

                    self.keypressed = False

                if event.type == pygame.KEYUP:
                    self.keypressed = True



            for layer in self.LAYERS:
                self.SCREEN.blit(layer,(200,0))

            self.SCREEN.blit(self.SIDEBAR, (0,0))
            self.labels(surface=self.SCREEN, text=f'X: {grid_mouse[0]} | Y: {grid_mouse[1]}', 
                        location=(self.SIDEBAR.get_width() + 10, 750))
            self.labels(surface=self.SCREEN, text=f'FPS: {round(self.FPS.get_fps(),2)}', 
                        location=(self.SIDEBAR.get_width() + 10, 780), font_size=13, color=(0,255,0))
            
            self.labels(surface=self.SCREEN, text=f'1: Place Tile', 
                        location=(215,15), font_size=13, color=(255,255,255))
            self.labels(surface=self.SCREEN, text=f'2: Delete Tile', 
                        location=(215,45), font_size=13, color=(255,255,255))
            self.labels(surface=self.SCREEN, text=f'3: Fill Selection', 
                        location=(365,15), font_size=13, color=(255,255,255))
            self.labels(surface=self.SCREEN, text=f'4: Tile Selection', 
                        location=(365,45), font_size=13, color=(255,255,255))
            

            self.labels(surface=self.SCREEN, text=f'Q: Next Layer', 
                        location=(555,15), font_size=13, color=(255,255,255))
            self.labels(surface=self.SCREEN, text=f'E: Prev Layer', 
                        location=(555,45), font_size=13, color=(255,255,255))

            self.labels(surface=self.SCREEN, text=f'Layer: {self.current_layer}', 
                        location=(885,20), font_size=20, color=(255,255,255))

            pygame.display.update()
            self.FPS.tick(100)


if __name__ == "__main__":
    Canvas().run()