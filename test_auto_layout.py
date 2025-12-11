#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test script for auto layout functionality.
This script creates a sample graph and tests the auto layout features.
"""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from Qt import QtWidgets
from NodeGraphQt import NodeGraph
from examples.nodes import basic_nodes

def create_test_graph():
    """Create a test graph with some nodes and connections."""
    app = QtWidgets.QApplication(sys.argv)
    
    # Create graph
    graph = NodeGraph()
    
    # Register nodes
    graph.register_nodes([
        basic_nodes.BasicNodeA,
        basic_nodes.BasicNodeB,
    ])
    
    # Set up context menu
    hotkey_path = Path(__file__).parent / 'examples' / 'hotkeys' / 'hotkeys.json'
    graph.set_context_menu_from_file(hotkey_path, 'graph')
    
    # Create some test nodes
    node1 = graph.create_node('nodes.basic.BasicNodeA', name='Node 1', pos=[0, 0])
    node2 = graph.create_node('nodes.basic.BasicNodeB', name='Node 2', pos=[100, 100])
    node3 = graph.create_node('nodes.basic.BasicNodeA', name='Node 3', pos=[200, -50])
    node4 = graph.create_node('nodes.basic.BasicNodeB', name='Node 4', pos=[300, 100])
    node5 = graph.create_node('nodes.basic.BasicNodeA', name='Node 5', pos=[400, 0])
    
    # Create connections to form a graph structure
    # node1 -> node2 -> node4
    # node1 -> node3 -> node4 -> node5
    output_port1 = node1.output_ports()[0] if node1.output_ports() else None
    input_port2 = node2.input_ports()[0] if node2.input_ports() else None
    input_port3 = node3.input_ports()[0] if node3.input_ports() else None
    
    if output_port1 and input_port2:
        output_port1.connect_to(input_port2)
    if output_port1 and input_port3:
        output_port1.connect_to(input_port3)
    
    output_port2 = node2.output_ports()[0] if node2.output_ports() else None
    input_port4 = node4.input_ports()[0] if node4.input_ports() else None
    if output_port2 and input_port4:
        output_port2.connect_to(input_port4)
    
    output_port3 = node3.output_ports()[0] if node3.output_ports() else None
    if output_port3 and input_port4:
        output_port3.connect_to(input_port4)
    
    output_port4 = node4.output_ports()[0] if node4.output_ports() else None
    input_port5 = node5.input_ports()[0] if node5.input_ports() else None
    if output_port4 and input_port5:
        output_port4.connect_to(input_port5)
    
    # Show the graph
    graph_widget = graph.widget
    graph_widget.resize(1200, 800)
    graph_widget.setWindowTitle("NodeGraphQt - Auto Layout Test")
    graph_widget.show()
    
    # Fit all nodes in view
    graph.fit_to_selection()
    
    print("\nAuto Layout Test Graph Created!")
    print("=" * 50)
    print("Test the following auto layout options from the Graph > Layout menu:")
    print("  1. Auto Layout (Spring) - Force-directed layout [Ctrl+Shift+L]")
    print("  2. Auto Layout (Circular) - Circular arrangement")
    print("  3. Auto Layout (Hierarchical) - Layered/spectral layout")
    print("\nNote: Make sure NetworkX is installed:")
    print("  pip install networkx")
    print("=" * 50)
    
    try:
        import networkx as nx
        print(f"\n✓ NetworkX {nx.__version__} is installed and ready!")
    except ImportError:
        print("\n✗ NetworkX is not installed. Please run: pip install networkx")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    create_test_graph()
