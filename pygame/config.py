WIN_WIDTH = 800
WIN_HEIGHT = 512
TILESIZE = 32
FPS = 60

Font = ('PressStart2P-Regular.ttf')

# Size of the camera view based on tile size and number of tiles to show
VISIBLE_TILES_X = 15
VISIBLE_TILES_Y = 11

CAM_WIDTH = VISIBLE_TILES_X * TILESIZE
CAM_HEIGHT = VISIBLE_TILES_Y * TILESIZE

PLAYER_LAYER = 4
NPC_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER = 1
TILESIZE = 32
FPS = 60

PLAYER_LAYER = 5
NPC_LAYER = 5
ROAD_LAYER = 2
BLOCK2_LAYER = 4
BLOCK_LAYER = 3
GROUND_LAYER = 1

PLAYER_SPEED = 2 
NPC_SPEED = 1

RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

tilemap = [
  'H.G.Y.Y.L.H.H.L.G.T.T.T.T',
  '.........................',
  '..................T.T.T.T',
  '.P...F...................',
  '22.2.2.2.2.2.2.2.2.4.T.T.',
  '.........................',
  'H.G.L.Y.G.H.G.T.T..1.T.T.',
  '..............T.T.........',
  '..................C1.T.T.',
  'T.T..X...................',
  '....Y..3.2.2B2.2.2.6.T.T.',
  'T.T......................',
  '.......1.......H.H.H.L.Y..',
  'T.T.G.....................',
  '.......1.......Y.G.G.L.Y',
  'T........................',
  '...3.2.6.T..........H.H.L',
  'T.......................',
  '...1..........C.....T.T.T',
  'T........................',
  '...5.2.2.2B2.2.2.4..T.T.T',
  '.........................',
  'H.G.H.G.L.L.Y.H..1..T.T.T',
  '.........................',
  '.................1..T.T.T',
  'T.M...........X..........',
  '.....2.2.2.2C2.2.6..S....',
  'T...E....................',
  '.........................',
  'H.L.L.Y.G.H.Y.Y.G.H.H.Y.G',
 
    # Add Nanay NPC
]
