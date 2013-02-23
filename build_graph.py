import sys
import json


# j : output of json.load() on an upverter openjson file
def build_graph(j):
  nodes = {}

  # build up nodes
  for ci in j["component_instances"]:
    # common node info
    id = ci["instance_id"]
    nodes[id] = {}
    nodes[id]["id"] = id
    nodes[id]["name"] = ci["attributes"]["refdes"]
    nodes[id]["pins"] = {}

    # resistor
    if j["components"][ci["library_id"]]["attributes"]["_type"] == "resistor":
      nodes[id]["type"] = "passive"
      nodes[id]["type-passive"] = "resistor"
      if "_resistance" in j["components"][ci["library_id"]]["attributes"]:
        nodes[id]["resistance"] = j["components"][ci["library_id"]]["attributes"]["_resistance"]

    # TODO LRC

    if "type" not in nodes[id]:
      nodes[id]["type"] = "component"


  # build up nets
  for n in j["nets"]:
    # assume net_id's and component id's don't overlap
    id = n["net_id"]
    nodes[id] = {}
    nodes[id]["id"] = id
    nodes[id]["pins"] = {}
    nodes[id]["type"] = "net"


    # build up pin list for this net
    pin_i = 1
    for p in n["points"]:
      for cc in p["connected_components"]:
        # net to other node
        nodes[id]["pins"][str(pin_i)] = {}
        nodes[id]["pins"][str(pin_i)]["node"] = cc["instance_id"]
        nodes[id]["pins"][str(pin_i)]["pin"] = cc["pin_number"]

        # other node to net
        nodes[cc["instance_id"]]["pins"][cc["pin_number"]] = {}
        nodes[cc["instance_id"]]["pins"][cc["pin_number"]]["node"] = id
        nodes[cc["instance_id"]]["pins"][cc["pin_number"]]["pin"] = str(pin_i)

        pin_i += 1

  return nodes


def print_graph(nodes):
  print "printing graph:"

  for id in nodes:
    node = nodes[id]
    print "  node:", node["id"]
    if "name" in node:
      print "    name:", node["name"]
    print "    type:", node["type"]

    if node["type"] == "passive" and node["type-passive"] == "resistor" and "resistance" in node:
      print "    resistance:", node["resistance"]

    print "    pins:"
    for i, p in node["pins"].items():
      print "      src pin:", i
      print "      dst pin:", p["pin"]
      print "      on node:", p["node"]

  print ""



def main():
  if len(sys.argv) < 2:
    print "you didn't specify a filename"
    return

  fp = open(sys.argv[1])
  j = json.load(fp)
  fp.close()

  nodes = build_graph(j)
  print_graph(nodes)


if __name__ == "__main__":
  main()
