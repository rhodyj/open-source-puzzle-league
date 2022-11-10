class Cursor: #the cursor uses indices from the on-game board (e.g. column 0 is NOT the border)
	def __init__(self, pos_x, pos_y):
		self.x = pos_x
		self.y = pos_y
		self.just_swapped = False #flag used in determining combo/chain data

	#standard functions for a data container object

	def set_x(self, pos_x):
		self.x = pos_x

	def set_y(self, pos_y):
		self.y = pos_y

	def get_x(self):
		return self.x
	
	def get_y(self):
		return self.y

	def set_just_swapped(self, val):
		self.just_swapped = val

	def get_just_swapped(self):
		return self.just_swapped

	#useful shorthand

	def move_up(self):
		self.y = self.y - 1

	def move_down(self):
		self.y = self.y + 1

	def move_left(self):
		self.x = self.x - 1

	def move_right(self):
		self.x = self.x + 1