class Cursor: #the cursor uses indices from the on-game board (e.g. column 0 is NOT the border)
	def __init__(self, pos_x, pos_y):
		self.x = pos_x
		self.y = pos_y