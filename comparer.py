import subprocess
import matplotlib.pyplot as plt
import sys
from lxml import html
from zss import simple_distance, Node
import networkx as nx


def make_html_nxgraph(parent, graph=None, ignore_comments=True):
  ''' Given an string containing HTML, return a networkx graph of the DOM
  '''
  if not graph:
    graph = nx.DiGraph()
  for node in parent.getchildren():
    # if the element is a comment, ignore it
    if ignore_comments and not isinstance(node.tag, basestring):
      continue
    graph.add_edge(parent, node)
    make_html_nxgraph(node, graph)
  return graph


def make_html_zssgraph(parent, graph=None, ignore_comments=True):
  ''' Given a string containing HTML, return a zss style tree of the DOM
  '''
  if not graph:
    graph = Node(parent.tag)
  for node in parent.getchildren():
    # if the element is a comment, ignore it
    if ignore_comments and not isinstance(node.tag, basestring):
      continue
    graph.addkid(Node(node.tag))
    make_html_zssgraph(node, graph)
  return graph
  

def domain_to_graph(fname, type="zss"):
  ''' a wrapper function that turns an html file to a dom graph
  '''
  fh = open(fname, 'r')
  content = fh.read()
  fh.close()

  if type == "zss":
    html_tag = html.document_fromstring(content)
    return make_html_zssgraph(html_tag)
  if type == "nx":
    html_tag = html.document_fromstring(content)
    return make_html_nxgraph(html_tag)


def draw_nx_graph(G, fname):
  dot_file = "%s.dot" % (fname)
  png_file = open("%s.png" % (fname), 'w')

  plt.title("%s" % (fname))
  pos=nx.graphviz_layout(G,prog='dot')
  nx.draw(G,pos,with_labels=False,arrows=False)
  plt.savefig("%s_pyplot.png" % (fname))

  nx.write_dot(G, dot_file)
  proc = subprocess.Popen(["dot", "-Tpng", dot_file], stdout=png_file)
  proc.wait()


def compare_graphs(g1, g2):
  ''' Given two graphs (zss trees) return a normalized distance between them
  '''
  g1_node_count = float( len(g1.get_children(g1)) ) # get the length of the tree starting at the root
  g2_node_count = float( len(g2.get_children(g2)) ) # ''
  dist = float(simple_distance(g1, g2))
  return 1 - (dist / (g1_node_count + g2_node_count))


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Usage: python comparer.py FILENAME FILENAME"
    exit()
  f1 = sys.argv[1]
  f2 = sys.argv[2]

  g1 = domain_to_graph(f1, type="nx")
  draw_nx_graph(g1, f1)
  g2 = domain_to_graph(f2, type="nx")
  draw_nx_graph(g2, f2)

  g1 = domain_to_graph(f1, type="zss")
  g2 = domain_to_graph(f2, type="zss")
  print compare_graphs(g1, g2)
