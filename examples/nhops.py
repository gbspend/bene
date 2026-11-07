from __future__ import print_function

import sys

sys.path.append('..')

#refer to bene/examples/simple.py

from src.sim import Sim
from src.scheduler import Scheduler
from src.packet import Packet
from networks.network import Network

#load config and set up simple start-to-end route
#first node listed in config file is "start", last node listed is "end"
#only creates a chain of one-way links for simplicity
def setupNHopsNetwork(config):
    net = Network(config)
    names = list(net.nodes)
    end = net.nodes[names[-1]]
    #last node's address facing the node before it
    end_address = end.get_address(names[-2])
    for i in range(len(names)-1):
        curr = net.nodes[names[i]]
        foll = net.nodes[names[i+1]]
        #check that link from curr to next exists
        link = curr.get_link(foll.hostname)
        if link is None:
            raise ValueError(f"no link from {curr.hostname} to {foll.hostname}")
        #set up forwarding entry from curr to next
        curr.add_forwarding_entry(address=end_address, link=link)
    return net

#get a node's address
#non-terminal nodes have one address PER LINK; so this only works for last node
def addr(node):
    if len(node.links) != 1:
        raise ValueError("node has more than one address")
    return node.links[0].address


class DelayHandler(object):
    @staticmethod
    def receive_packet(packet):
        print((Sim.scheduler.current_time(),
               packet.ident,
               packet.created,
               Sim.scheduler.current_time() - packet.created,
               packet.transmission_delay,
               packet.propagation_delay,
               packet.queueing_delay))


def main():
    Sim.scheduler = Scheduler()

    # setup network
    net = setupNHopsNetwork('../networks/one-hop.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')

    # setup app
    d = DelayHandler()
    n2.add_protocol(protocol="delay", handler=d)

    # send one packet
    p = Packet(destination_address=addr(n2), ident=1, protocol='delay', length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()

if __name__ == '__main__':
    main()
