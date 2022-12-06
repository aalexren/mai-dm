import sys
import networkx as nx
import matplotlib.pyplot as plt
import random
from networkx.algorithms import bipartite
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from MainWindow import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
   def __init__(self, *args, obj=None, **kwargs):
      super(MainWindow, self).__init__(*args, **kwargs)
      self.setupUi(self)
      
      fg = self.frameGeometry()
      cp = QtWidgets.QDesktopWidget().availableGeometry().center()
      fg.moveCenter(cp)
      self.move(fg.topLeft())
      QtWidgets.QMessageBox.about(self, "Инфо", "Граф задаётся матрицей инцидентности")

      self.btnExit.clicked.connect(self.exit)
      self.btnSetupGraph.clicked.connect(self.setup_graph)
      self.btnColorGraph.clicked.connect(self.color_graph)
      self.btnShowGraph.hide()

      self.rows_, self.cols_ = 0, 0
      self.lblColors.hide()

      self.graph_stack = []

   def setup_graph(self):
      rows, cols = self.spboxVertex.value(), self.spboxEdges.value()
      self.rows_ = rows
      self.cols_ = cols
      self.tblMatrix.setRowCount(rows+1)
      self.tblMatrix.setColumnCount(cols+1)

      for i in range(rows):
         item = QtWidgets.QTableWidgetItem(f"v{i+1}")
         item.setFlags(QtCore.Qt.ItemIsEnabled)
         self.tblMatrix.setItem(i+1,0, item)
      for i in range(cols):
         item = QtWidgets.QTableWidgetItem(f"e{i+1}")
         item.setFlags(QtCore.Qt.ItemIsEnabled)
         self.tblMatrix.setItem(0,i+1, item)

   def show_graph(self):
      try:
         plt.close('all')
         G = self.graph_stack[0][0]
         pos = self.graph_stack[0][1]
         nx.draw(G, pos=pos, with_labels=True, font_weight='light')
         plt.show()
      except:
         pass

   def color_graph(self):
      plt.close('all')
      model = self.tblMatrix.model()
      graph = []
      for i in range(1, model.columnCount()):
         graph.append([])
         for j in range(1, model.rowCount()):
            index = model.index(j, i)
            data = str(model.data(index))
            if data == '1':
               graph[i-1].append(j-1)
         sorted(graph[i-1])
      G = nx.Graph()
      G.add_nodes_from([f'v{i+1}' for i in range(0, self.rows_)], bipartite=0)
      G.add_nodes_from([f'e{i+1}' for i in range(0, self.cols_)], bipartite=1)
      edges_ = []
      for i in range(0, len(graph)):
         for j in range(0, len(graph[i])):
               edges_.append((f'v{graph[i][j]+1}', f'e{i+1}'))
      G.add_edges_from(edges_)
      u = [n for n in G.nodes if n.startswith('v')]
      X, Y = bipartite.sets(G, top_nodes=u)
      pos = dict()
      pos.update( (n, (1, i)) for i, n in enumerate(X) ) # put nodes from X at x=1
      pos.update( (n, (2, i)) for i, n in enumerate(sorted(Y)) ) # put nodes from Y at x=2

      matrix = {}
      for k in range(self.rows_):
         temp = []
         for j in range(1, model.columnCount()):
            if str(model.data(model.index(k+1, j))) == '1':
               for h in range(1, model.rowCount()):
                  if str(model.data(model.index(h, j))) == '1' and h != k+1:
                     if (h-1) not in temp:
                        temp.append(h-1)
         matrix[k] = temp
      
      matrix = {k: v for k, v in sorted(matrix.items(), key=lambda item: len(item[1]), reverse=True)}

      colors = get_colors(matrix)
      for k, v in colors.items():
         nx.draw_networkx_nodes(G, nodelist=[f'v{k+1}'], node_color='#%02x%02x%02x' % v, pos=pos)
      nx.draw_networkx_labels(G, pos=pos)
      count_colors = len(set(colors.values()))
      self.lblColors.show()
      self.lblColors.setText(f"Цветов получилось: {count_colors}")

      nx.draw_networkx_nodes(G, nodelist=[f'e{i+1}' for i in range(self.cols_)], pos=pos)
      nx.draw_networkx_edges(G, pos=pos)
      plt.show()

   def exit(self):
      self.close()


def get_colors(matrix):
   colors = gen_colors(len(matrix))
   colored = {i: None for i in range(len(matrix))} # vertex -> color
   for clr in colors:
      find = False
      for key in matrix.keys():
         if colored[key] == None:
            nxt = key
            find = True
            break
      if find == False:
         break
      colored[nxt] = clr
      for v in matrix.keys():
         if v == nxt or colored[v] != None:
            continue
         crack = False
         for s in matrix[v]:
            if colored[s] == clr:
               crack = True
               break
         if crack == False and colored[v] == None:
            colored[v] = clr
   return colored


def gen_colors(n):
   ret = []
   r = int(random.random() * 256)
   g = int(random.random() * 256)
   b = int(random.random() * 256)
   step = 256 / n
   for i in range(n):
      r += step
      g += step
      b += step
      r = int(r) % 256
      g = int(g) % 256
      b = int(b) % 256
      ret.append((r,g,b)) 
   return ret

def uniq_color(vertex, arr, colored):
   for i in arr:
      if colored[vertex] == colored[i]:
         return False
   return True

def main():
   app = QtWidgets.QApplication(sys.argv)

   window = MainWindow()
   window.show()
   app.exec()

if __name__ == '__main__':
   try:
      main()
   except Exception as ex:
      print(ex)