# Auto Layout Feature

## Overview

The NodeGraphQt project now includes advanced auto layout functionality powered by NetworkX, providing multiple algorithms to automatically arrange nodes in your graph for better visualization.

## Features

Three different layout algorithms are available:

### 1. **Spring Layout (Force-Directed)**
- **Shortcut**: `Ctrl+Shift+L`
- **Best for**: General-purpose graphs, network visualizations
- **Description**: Uses a force-directed algorithm where nodes repel each other while connected nodes are attracted. This creates a natural, balanced layout.
- **Algorithm**: NetworkX's `spring_layout` with Fruchterman-Reingold force-directed algorithm

### 2. **Circular Layout**
- **Best for**: Cyclic graphs, showing all nodes equally
- **Description**: Arranges all nodes in a perfect circle, useful for visualizing cycles and symmetric relationships.
- **Algorithm**: NetworkX's `circular_layout`

### 3. **Hierarchical Layout**
- **Best for**: Directed graphs, dependency trees, workflow visualization
- **Description**: Creates a layered layout that emphasizes the hierarchical structure of the graph.
- **Algorithm**: NetworkX's `spectral_layout` (falls back to `shell_layout` if needed)

## Installation

To use the auto layout features, you need to install NetworkX:

```bash
pip install networkx
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Via Menu
1. Right-click on the graph canvas
2. Navigate to: **Graph > Layout**
3. Choose one of the auto layout options:
   - Auto Layout (Spring)
   - Auto Layout (Circular)
   - Auto Layout (Hierarchical)

### Via Keyboard Shortcut
- Press `Ctrl+Shift+L` for Spring Layout (most commonly used)

### On Selected Nodes
- Select specific nodes you want to layout
- Use any of the layout menu options
- Only the selected nodes will be rearranged

### On All Nodes
- Make sure no nodes are selected
- Use any of the layout menu options
- All nodes in the graph will be rearranged

## How It Works

The auto layout system:

1. **Builds a graph structure** from your node connections using NetworkX
2. **Calculates optimal positions** using the selected algorithm
3. **Applies positions** while maintaining the center point of your node group
4. **Handles backdrop nodes** by wrapping them around contained nodes after layout
5. **Supports undo/redo** for all layout operations

## Technical Details

### NetworkX Integration
- **Library**: NetworkX >= 2.5
- **Graph Type**: DirectedGraph (DiGraph) to respect connection directionality
- **Scale Parameters**: Optimized for typical node graph dimensions (400-500 units)

### Layout Parameters

#### Spring Layout
- `k=2.0`: Optimal distance between nodes (higher = more spread)
- `iterations=50`: Quality of layout (higher = better but slower)
- `scale=500`: Overall size of the layout

#### Circular Layout
- `scale=400`: Radius of the circle

#### Hierarchical Layout
- `scale=500`: Overall size for spectral layout
- `scale=400`: Fallback size for shell layout

## Testing

Run the test script to see the auto layout in action:

```bash
python test_auto_layout.py
```

This creates a sample graph with 5 nodes and connections, allowing you to test all layout algorithms interactively.

## Comparison with Existing Auto Layout

NodeGraphQt already has built-in auto layout functions (`layout_graph_up` and `layout_graph_down`) that work well for hierarchical, linear graphs. The new NetworkX-based layouts provide:

**Advantages**:
- Better handling of complex, non-linear graph structures
- Multiple layout algorithms for different use cases
- More natural visual appearance for interconnected nodes
- Better spacing and distribution

**When to use each**:
- **Original auto layout**: Linear workflows, clear upstream/downstream relationships
- **Spring layout**: Complex interconnected graphs, network visualizations
- **Circular layout**: Cyclic graphs, showing symmetry
- **Hierarchical layout**: Directed acyclic graphs (DAGs), dependency trees

## Future Enhancements

Potential improvements for future versions:

1. **PyGraphviz Integration**: For production-quality hierarchical layouts (dot, neato, etc.)
2. **igraph Support**: Better performance for large graphs (1000+ nodes)
3. **Custom Parameters**: UI to adjust k, iterations, and scale parameters
4. **Animation**: Smooth transitions between layouts
5. **Layout Presets**: Save and load custom layout configurations
6. **Collision Detection**: Prevent node overlap in dense graphs

## Troubleshooting

### "NetworkX is required" Error
Install NetworkX:
```bash
pip install networkx
```

### Layout Doesn't Look Good
- Try a different algorithm - each works best for different graph structures
- For hierarchical graphs: Use Hierarchical Layout
- For complex networks: Use Spring Layout
- For simple cycles: Use Circular Layout

### Nodes Too Close/Far Apart
The spacing is optimized for typical graphs. Future versions will allow customization of spacing parameters.

## References

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Graph Layout Algorithms](https://en.wikipedia.org/wiki/Graph_drawing)
- [Force-Directed Graph Drawing](https://en.wikipedia.org/wiki/Force-directed_graph_drawing)
