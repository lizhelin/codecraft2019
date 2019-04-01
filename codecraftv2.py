# -*- coding:utf-8 -*-
import os
# import networkx as nx
import matplotlib.pyplot as plt
import heapq
import sys

carlist = list()
cardict = {}
roadlist = list()
roaddict = {}
crosslist = list()
crossdict = {}
graphdict = {}
waylist = list()
waydict = {}
starttime = list()
wayidlist = list()


def cartodict(dir):
    global carlist, cardict
    file = open(dir)
    alllines = file.readlines()
    for line in alllines[1:] :
        line = line.replace(' ', '')
        line = line.replace('\n', '')
        carlist.append(line[1:-1].split(','))         
    for item in carlist :
        cardict[item[0]] = {'from':item[1], 'to':item[2], 'speed':item[3],
                             'plantime':item[4]}

def roadtodict(dir):
    global roadlist, roaddict
    file = open(dir)
    alllines = file.readlines()
    for line in alllines[1:] :
        line = line.replace(' ', '')
        line = line.replace('\n', '')
        roadlist.append(line[1:-1].split(','))         
    for item in roadlist :
        roaddict[item[0]] = {'length':item[1], 'speed':item[2], 'channel':item[3],
                             'from':item[4], 'to':item[5], 'isDuplex':item[6], 'weight':0}

        
def crosstodict(dir):
    global crosslist, crossdict
    file = open(dir)
    alllines = file.readlines()
    for line in alllines[1:] :
        line = line.replace(' ', '')
        line = line.replace('\n', '')
        crosslist.append(line[1:-1].split(','))
    # print(crosslist)
    for item in crosslist :
        crossdict[item[0]] = item[1:]  


# print(roaddict)
# print(crossdict)
# print(cardict)
def graphtodict(crossdict, roaddict):
    for key in crossdict:  # 遍历节点id
        graphlist = {}
        graphlist.clear()
        for item in crossdict.get(key):  # 遍历该节点的所有道路id
            if item != '-1' :  # 排除不连通的道路
                if roaddict.get(item).get('isDuplex') == '1' :
                    if roaddict.get(item).get('from') == key:  # 如果道路的出发节点和该节点id相同 则将到达节点加入列表
                        graphlist[roaddict.get(item).get('to')] = int(roaddict.get(item).get('length'))/int(roaddict.get(item).get('speed'))/int(roaddict.get(item).get('channel'))/2
                    
                    elif roaddict.get(item).get('to') == key:  # 如果道路的到达节点和该节点id相同 则将出发节点加入列表
                        for roadid in roaddict :
                            if (roaddict.get(roadid).get('to') == key) & (roaddict.get(roadid).get('from') 
                                                                            == roaddict.get(item).get('from')):
                                graphlist[roaddict.get(item).get('from')] = int(roaddict.get(roadid).get('length'))/int(roaddict.get(roadid).get('speed'))/int(roaddict.get(item).get('channel'))/2
                else :
                    if roaddict.get(item).get('from') == key:  # 如果道路的出发节点和该节点id相同 则将到达节点加入列表
                        graphlist[roaddict.get(item).get('to')] = int(roaddict.get(item).get('length'))/int(roaddict.get(item).get('speed'))/int(roaddict.get(item).get('channel'))
        graphdict[key] = graphlist

'''
def drawpic(graphdict):
    G = nx.DiGraph()
    for key in graphdict:
        for item in graphdict[key]:
            G.add_edge(key, item, len=10)
    
    # pos = nx.spring_layout(G,k = 0.1,iterations = 100)
    nx.draw(G, with_labels=True, pos=nx.spectral_layout(G), arrows=True)
    plt.show()
'''


class Graph:
    
    def __init__(self):
        self.vertices = {}

    def clear_vertex(self):
        self.vertices.clear()
        
    def remove_vertex(self, key):
        self.vertices.pop(key)

    def add_vertex(self, name, edges):
        self.vertices[name] = edges
    
    def shortest_path(self, start, finish):
        distances = {}  # Distance from start to node
        previous = {}  # Previous node in optimal path from source
        nodes = []  # Priority queue of all nodes in Graph

        for vertex in self.vertices:
            if vertex == start:  # Set root node as distance of 0
                distances[vertex] = 0
                heapq.heappush(nodes, [0, vertex])
            else:
                distances[vertex] = sys.maxsize
                heapq.heappush(nodes, [sys.maxsize, vertex])
            previous[vertex] = None
        
        while nodes:
            smallest = heapq.heappop(nodes)[1]  # Vertex in nodes with smallest distance in distances
            if smallest == finish:  # If the closest node is our target we're done so print the path
                path = []
                while previous[smallest]:  # Traverse through nodes til we reach the root which is 0
                    path.append(smallest)
                    smallest = previous[smallest]
                return path
            if distances[smallest] == sys.maxsize:  # All remaining vertices are inaccessible from source
                break
            
            for neighbor in self.vertices[smallest]:  # Look at all the nodes that this vertex is attached to
                alt = distances[smallest] + self.vertices[smallest][neighbor]  # Alternative path distance
                if alt < distances[neighbor]:  # If there is a new shortest path update our priority queue (relax)
                    distances[neighbor] = alt
                    previous[neighbor] = smallest
                    for n in nodes:
                        if n[1] == neighbor:
                            n[0] = alt
                            break
                    heapq.heapify(nodes)
        return distances
        
    def __str__(self):
        return str(self.vertices)

    
def writefile(dir, info):
    filepath = dir
    file = open(filepath, 'a')
    file.write(info + '\n')
    file.close()


if __name__ == '__main__':
    dir_r = 'road.txt'
    dir_c = 'cross.txt'
    dir_car = 'car.txt'
    dir_txt = 'D:\\answer.txt'
    roadtodict(dir_r)
    crosstodict(dir_c)
    cartodict(dir_car)
    carlist.clear()
    carlist = sorted(cardict.items(),key = lambda item:item[1].get('speed'),reverse=True)
    cardict.clear()
    for i in range(len(carlist)) :
        cardict[carlist[i][0]] = carlist[i][1]
    graphtodict(crossdict, roaddict)
    #print(graphdict.get('1'))
    g = Graph()
    # 按照新权重添加边，重新规划最优路径
    g.clear_vertex()
    count = 0
    for key in graphdict :
        g.add_vertex(key, graphdict.get(key))
    for carid in cardict:
        wayidlist.clear()
        waylist = g.shortest_path(cardict.get(carid).get('from'), cardict.get(carid).get('to'))
        waylist.append(cardict.get(carid).get('from'))  # 得到完整路径
        waylist.reverse()  # 对路径反向排序
        # print(cardict.get(carid).get('from'),cardict.get(carid).get('to'),waylist)
        for item in waylist[:-1]:
            index = waylist.index(item)
            to = waylist[index + 1]
            for roadid in roaddict:
                if (roaddict.get(roadid).get('from') == item) & (roaddict.get(roadid).get('to') == to):
                    wayidlist.append(roadid)
                elif (roaddict.get(roadid).get('from') == to) & (roaddict.get(roadid).get('to') == item) & (roaddict.get(roadid).get('isDuplex') == '1') :
                    wayidlist.append(roadid)
        # print(cardict.get(carid).get('from'),cardict.get(carid).get('to'),wayidlist)
        
        initialtime = int(cardict.get(carid).get('plantime'))  # 初始出发时间
        #bias = starttime.index(cardict.get(carid).get('speed'))  # 时间偏置
        #finaltime = initialtime + bias * 1000  # 最终出发时间
        if cardict.get(carid).get('speed') == '8' :
            finaltime = initialtime+int(count//500)*30
        elif cardict.get(carid).get('speed') == '6' :
            finaltime = initialtime+int(count//500)*30
        elif cardict.get(carid).get('speed') == '4' :
            finaltime = initialtime+int(count//500)*30
        elif cardict.get(carid).get('speed') == '2' :
            finaltime = initialtime+int(count//500)*30
        count += 1
        # print(initialtime,bias,type(finaltime))
        finalstr = '(' + carid + ',' + str(finaltime) + ',' + ','.join(wayidlist) + ')'
        # print(finalstr)
        writefile(dir_txt, finalstr)

    # drawpic(graphdict)
