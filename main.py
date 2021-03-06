from node import Node
import numpy as np

class Input(Node):

	def __init__(self):
		Node.__init__(self)

	def forward(self):
		
		pass

	def backward(self):
		self.gradients = {self:0}

		for n in self.outbound_nodes:
			self.gradients[self] += n.gradients[self]


class Linear(Node):
	def __init__(self, inputs, weights, bias):
		Node.__init__(self, [inputs, weights, bias])

	def forward(self):
		i = self.inbound_nodes[0].value
		w = self.inbound_nodes[1].value
		b = self.inbound_nodes[2].value

		self.value = np.dot(i, w) + b

	def backward(self):
		self.gradients = {n:np.zeros_like(n.value) for n in self.inbound_nodes}

		for n in self.outbound_nodes:
			#get the partial of the cost wrt this node
			grad_cost = n.gradients[self]
			# Set the partial of the loss with respect to this node's inputs.
			self.gradients[self.inbound_nodes[0]] += np.dot(grad_cost, self.inbound_nodes[1].value.T)
			# Set the partial of the loss with respect to this node's weights.
			self.gradients[self.inbound_nodes[1]] += np.dot(self.inbound_nodes[0].value.T, grad_cost)
			# Set the partial of the loss with respect to this node's bias.
			self.gradients[self.inbound_nodes[2]] += np.sum(grad_cost, axis=0, keepdims=False)

class Sigmoid(Node):
	def __init__(self, node):
		Node.__init__(self, [node])

	def _sigmoid(self, x):

		return 1/(1+np.exp(-x))

	def forward(self):

		x_value = self.inbound_nodes[0].value

		self.value = self._sigmoid(x_value)

	def backward(self):

		self.gradients = {n:np.zeros_like(n.value) for n in self.inbound_nodes}
		for n in self.outbound_nodes:
			grad_cost = n.gradients[self]
			sigmoid = self.value
			self.gradients[self.inbound_nodes[0]] += sigmoid*(1-sigmoid)*grad_cost

class MSE(Node):

	def __init__(self, y, a):
		Node.__init__(self, [y, a])

	def forward(self):
		y = self.inbound_nodes[0].value.reshape(-1, 1)
		a = self.inbound_nodes[1].value.reshape(-1, 1)
		self.m = self.inbound_nodes[0].value.shape[0]
		self.diff = (y-a)
		self.value = np.mean((np.square(self.diff)))

	def backward(self):
		self.gradients[self.inbound_nodes[0]] = (2/self.m)*self.diff
		self.gradients[self.inbound_nodes[1]] = (-2/self.m)*self.diff

class CrossEnt(Node):

	def __init__(self, y, a):
		Node.__init__(self, [y, a])

	def forward(self):
		y = self.inbound_nodes[0].value.reshape(-1, 1)
		a = self.inbound_nodes[1].value.reshape(-1, 1)
		self.log = np.log(a)
		self.value = -np.sum(y*self.log)

	def backward(self):
		y = self.inbound_nodes[0].value.reshape(-1, 1)
		a = self.inbound_nodes[1].value.reshape(-1, 1)
		self.gradients[self.inbound_nodes[0]] = -y/a
		self.gradients[self.inbound_nodes[1]] = -self.log

def topological_sort(feed_dict):
    """
    Sort generic nodes in topological order using Kahn's Algorithm.

    `feed_dict`: A dictionary where the key is a `Input` node and the value is the respective value feed to that node.

    Returns a list of sorted nodes.
    """

    input_nodes = [n for n in feed_dict.keys()]

    G = {}
    nodes = [n for n in input_nodes]
    while len(nodes) > 0:
        n = nodes.pop(0)
        if n not in G:
            G[n] = {'in': set(), 'out': set()}
        for m in n.outbound_nodes:
            if m not in G:
                G[m] = {'in': set(), 'out': set()}
            G[n]['out'].add(m)
            G[m]['in'].add(n)
            nodes.append(m)

    L = []
    S = set(input_nodes)
    while len(S) > 0:
        n = S.pop()

        if isinstance(n, Input):
            n.value = feed_dict[n]

        L.append(n)
        for m in n.outbound_nodes:
            G[n]['out'].remove(m)
            G[m]['in'].remove(n)
            # if no other incoming edges add to S
            if len(G[m]['in']) == 0:
                S.add(m)
    return L

def forward_and_backward(graph):

	for n in graph:
		n.forward()

	for n in graph[::-1]:
		n.backward()

def sgd_update(trainables, learning_rate=1e-2):

	for t in trainables:
		partial = t.gradients[t]
		t.value -= learning_rate*partial

def RMSProp(trainables,g , learning_rate=1e-2):
	eps = 1e-8
	beta = 0.9
	for t in trainables:
		dl = t.gradients[t]
		g[t] = beta*g[t] + (1-beta)*(dl**2)
		t.value -= learning_rate*dl/(np.sqrt(g[t])+eps)
