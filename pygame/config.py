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
  'H.G......................',
  '.........................',
  '......T.T.T.T.............',
  '.1.F..........X..........',
  '.P........E..............',
  '.5.2.2.2.2.2.2.2.4.......',
  '...............N.........',
  'H.G.L.Y.G.H.G.TT.1.......',
  '..............TT.A.......',
  '.................1.......',
  '............K............',
  '.......3.2.2.2.2.6.......',
  '.........S...............',
  '..B....1..................',
  '.........................',
  '.......1.....Z............',
  '.........................',
  '.........................',
  '.........................',
  '.........................',
  '.........................',
  'H.G.H.G..................',
  '.........................',
  '..............M..........',
  '...........E.............',
  '.........................',
  '.........................',  # Add Bata NPC
  '.........................',  # Add Idle NPC
  '.........................',  # Add Aling Nena NPC
    # Add Nanay NPC
]
