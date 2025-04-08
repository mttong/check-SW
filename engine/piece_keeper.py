DEFAULT_STARTING_POSITIONS = {
	"a1": 'wr1',
	"b1": 'wn2',
	"c1": 'wb1',
	"d1": 'wq',
	"e1": 'wk',
	"f1": 'wb2',
	"g1": 'wn2',
	"h1": 'wr2',
	"a2": 'wp1',
	"b2": 'wp2',
	"c2": 'wp3',
	"d2": 'wp4',
	"e2": 'wp5',
	"f2": 'wp6',
	"g2": 'wp7',
	"h2": 'wp8',
	
	"a8": 'br1',
	"b8": 'bn2',
	"c8": 'bb1',
	"d8": 'bq',
	"e8": 'bk',
	"f8": 'bb2',
	"g8": 'bn2',
	"h8": 'br2',
	"a7": 'bp1',
	"b7": 'bp2',
	"c7": 'bp3',
	"d7": 'bp4',
	"e7": 'bp5',
	"f7": 'bp6',
	"g7": 'bp7',
	"h7": 'bp8',
}

class PieceKeeper:
	def __init__(self):
		self.pieces = DEFAULT_STARTING_POSITIONS
		self.white_discard = 0
		self.black_discard = 0
		
	def _get_discard(self, white):
		if white:
			self.white_discard += 1
			if self.white_discard < 9:
				return 'j' + str(self.white_discard)
			else:
				return 'i' + str(self.white_discard - 8)
		else:
			self.black_discard += 1
			if self.black_discard < 9:
				return 'k' + str(self.black_discard)
			else:
				return 'l' + str(self.black_discard - 8)
		
	def move(self, from_coord, to_coord):
		return_move = []
		from_piece = self.pieces[from_coord]
		del self.pieces[from_coord]
		
		if to_coord in self.pieces:
			to_piece = self.pieces[to_coord]
			self.pieces[to_coord] = from_piece
			discard_move = self._get_discard(to_piece[0] == 'w')
			self.pieces[discard_move] = to_piece
			return_move.append([[to_coord, discard_move], to_piece[1]])
		
		return_move.append([[from_coord, to_coord], from_piece[1]])
		self.pieces[to_coord] = from_piece
		
		return return_move
			
		
			
		
			
			
			
		
		
		
	

