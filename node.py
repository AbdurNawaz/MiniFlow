class Node:
	def __init__(self, inbound_nodes=[]):
		#nodes from which this node recieves values
		self.inbound_nodes = inbound_nodes
		#node to which this node passes values
		self.outbound_nodes = []

		self.value = None
		#Adding this node as an outbound node for each of its inbound node
		for n in inbound_nodes:
			n.outbound_nodes.append(self)

	def forward(self):

		raise NotImplementedError



