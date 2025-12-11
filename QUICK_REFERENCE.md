# Quick Reference: Auto Layout Feature

## 🚀 Quick Start

**Keyboard Shortcut**: Press `Ctrl+Shift+L` for instant Spring Layout

**Menu Access**: Right-click → Graph → Layout → Choose algorithm

## 📊 Choose Your Algorithm

### 🌟 Spring Layout (Ctrl+Shift+L)
**Use when:** You have a general graph with interconnected nodes
**Result:** Natural, balanced layout with good spacing

### ⭕ Circular Layout
**Use when:** Showing cycles, loops, or symmetric relationships
**Result:** All nodes arranged in a perfect circle

### 📊 Hierarchical Layout
**Use when:** Visualizing DAGs, dependencies, or hierarchies
**Result:** Layered structure emphasizing flow

## 💡 Tips

- **Select nodes** before applying layout to arrange only those nodes
- **No selection** = layout all nodes in the graph
- All layouts support **Undo/Redo** (Ctrl+Z / Ctrl+Y)
- Works with **backdrop nodes** - they'll wrap around their contents

## ⚙️ Installation

If you get an error about NetworkX:
```bash
pip install networkx
```

## 🎯 Common Use Cases

| Scenario | Best Layout |
|----------|-------------|
| Web/network diagram | Spring |
| State machine | Circular |
| Workflow/pipeline | Hierarchical |
| Mind map | Spring |
| Process flow | Hierarchical |
| Dependency graph | Hierarchical |
| Social network | Spring |

## 🔄 Compare with Built-in Layouts

**Built-in** (L / Ctrl+L):
- Simple hierarchical arrangement
- Fast for linear workflows

**New NetworkX** (Ctrl+Shift+L):
- Multiple algorithms
- Better for complex graphs
- More natural appearance

## 📖 Full Documentation

See `AUTO_LAYOUT.md` for complete documentation including:
- Algorithm details
- Technical parameters
- Troubleshooting
- Future enhancements
