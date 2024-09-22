
#code adapted and referred from Patrick Lester, Nicholas Swift, Ryan Collingwood, Ciril Lom, and others: https://gist.github.com/ryancollingwood/32446307e976a11a1185a5394d6657bc
from warnings import warn
import heapq
from itertools import product
import numpy as np
import sys

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position
    
    def __repr__(self):
      return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
      return self.f < other.f
    
    # defining greater than for purposes of heap queue
    def __gt__(self, other):
      return self.f > other.f

    def return_path(self):
        path = []
        current = self
        while current is not None:
            path.append(current.position)
            current = current.parent
        return path[::-1]
    
    def euclidean_distance(self, other):
        return round(sum([(self.position[i] - other.position[i])**2 for i in range(len(self.position))]) ** 0.5, 3)

    def is_outside(self, maze):
        def check_dimension(dim_maze, position, dim=0):
            if dim >= len(position):
                return False
            
            if position[dim] < 0 or position[dim] >= len(dim_maze):
                return True
            
            return check_dimension(dim_maze[position[dim]], position, dim + 1)
        
        return check_dimension(maze, self.position)

    def is_wall(self, maze):
        def navigate_dimension(dim_maze, position, dim=0):
            if dim == len(position) - 1:
                return dim_maze[position[dim]] == 0
            
            return navigate_dimension(dim_maze[position[dim]], position, dim + 1)
        
        return navigate_dimension(maze, self.position)

def astar(maze, start, end):
    dimension = len(maze.shape)
    if len(start) != dimension or len(end) != dimension:
        raise ValueError("Start and end must have the same number of dimensions as the maze")

    # Create start and end node
    start_node = Node(None, start)
    end_node = Node(None, end)

    closed_list = []
    open_list = []
    heapq.heapify(open_list) #create priority queue for open list
    heapq.heappush(open_list, start_node)

    outer_iterations = 0
    # max_iterations = (maze.size // 2)
    max_iterations = (maze.size*2)
    # max_iterations = (1000)

    # Define the adjacent squares (including diagonals)
    # adjacent_squares = [c for c in product((-1, 0, 1), repeat=dimension) if any(c)]
    
    # Define the adjacent squares (only consider bottom, right, left, top)
    adjacent_squares = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    # Loop until you find the end
    while len(open_list) > 0:
        outer_iterations += 1

        if outer_iterations > max_iterations:# if we cannot find by searching half the maze, we give up
            warn("giving up on pathfinding. too many iterations")
            return current_node.return_path()
        
        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        if current_node == end_node and open_list[0].f >= current_node.f:
            #! we are done
            return current_node.return_path()

        for new_position in adjacent_squares:
            # Get node position
            node_position = tuple([current_node.position[i] + new_position[i] for i in range(dimension)])
            new_node = Node(current_node, node_position)

            if new_node.is_outside(maze):
                continue

            if new_node.is_wall(maze):
                continue

            if new_node in closed_list:
                continue

            child = new_node #the new node is a valid child of the current_node
            #calculate the heuristic
            cost = sum([(child.position[i] - current_node.position[i])**2 for i in range(dimension)]) ** 0.5
            child.g = current_node.g + cost
            child.h = child.euclidean_distance(end_node)
            child.f = child.g + child.h

            #add or update the child to the open list
            if child in open_list: 
                i = open_list.index(child) 
                if child.g < open_list[i].g:
                    # update the node in the open list
                    open_list[i] = child
            else:
                heapq.heappush(open_list, child)

    warn("Couldn't get a path to destination")
    return None


def a_star_search_returnMap(maze,start,end):
    print('a star search computing, trying to return whole map')
    #ensure maze is in int type
    maze=(maze).astype(int)

    #running the actual a star algorithm
    path = astar(maze, start, end)

    #mark path in the global map as 999 to mark where the path is
    for iter in path:
        maze[iter]=1028

    #return a maze in a numpy array with an updated path
    maze=np.asarray(maze).astype(int)
    return maze

def a_star_search_returnPath(maze,start,end):
    print('a star search computing')
    #ensure maze is in int type
    maze=(maze).astype(int)

    #running the actual a star algorithm
    path = astar(maze, start, end)

    #directly return an array of tuples of shortest path found in the A*
    return path

start = (40,100)
end= (30,103)
np.set_printoptions(threshold=sys.maxsize)
a_array= np.genfromtxt('C:/Users/aravn/Desktop/Courses/UIUC/CS437 - Internet of Things/Lab Repo/cs437/test.csv',delimiter=',').astype(int)
print (a_array.shape)
x =a_star_search_returnMap(a_array,start,end)

print(a_array)
print(x)