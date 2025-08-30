# John Qubit - VQE Quantum Simulator Dashboard

A real-time quantum simulation dashboard for Variational Quantum Eigensolvers (VQE) with multiple optimization methods.

## 🚀 Features

- **Real-time VQE Simulation**: Live energy convergence visualization with 2-second updates
- **Multiple VQE Methods**: 
  - Normal VQE
  - VQE + UCCSD + Hybrid Optimizer
  - VQE + UCCSD + Hybrid Optimizer + ZNE (Zero Noise Extrapolation)
- **Auto-convergence Detection**: Simulation stops when energy differences become minimal
- **Dynamic Graph Scaling**: Y-axis automatically adjusts to show all energy values
- **Energy Summary Panel**: Real-time energy values for all methods
- **Clean Modern UI**: Professional interface with responsive design

## 📊 Dashboard Layout

```
┌─────────────────┬─────────────────┐
│   Normal VQE    │ VQE+UCCSD+Hybrid│
│     Chart       │      Chart      │
├─────────────────┼─────────────────┤
│VQE+UCCSD+Hybrid │   Energy        │
│    +ZNE Chart   │   Summary       │
└─────────────────┴─────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Dependencies
```bash
pip install tkinter matplotlib numpy
```

### Quick Start
1. Clone this repository:
```bash
git clone https://github.com/[your-username]/John-Qubit.git
cd John-Qubit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
python vqe_simulator_dashboard.py
```

## 🎮 Usage

1. **Launch the Application**: Run the Python script to open the dashboard
2. **Start Simulation**: Click the "Run Simulation" button to begin
3. **Watch Convergence**: Observe real-time energy optimization across all VQE methods
4. **Auto-Stop**: Simulation automatically stops when all methods converge
5. **Restart**: Click "Run Simulation" again to restart with fresh data

## 🔬 VQE Methods Explained

### Normal VQE
- Basic Variational Quantum Eigensolver
- Slower convergence with more noise
- Good baseline for comparison

### VQE + UCCSD + Hybrid Optimizer
- Unitary Coupled Cluster Singles and Doubles ansatz
- Hybrid classical-quantum optimization
- Faster convergence with reduced noise

### VQE + UCCSD + Hybrid Optimizer + ZNE
- All features of VQE + UCCSD + Hybrid
- Zero Noise Extrapolation for error mitigation
- Best performance with highest accuracy

## 📈 Features in Detail

### Real-time Updates
- **2-second intervals** for smooth visualization
- **Exponential convergence** simulation with method-specific characteristics
- **Live energy tracking** with precise Hartree unit display

### Convergence Detection
- **Automatic stopping** when energy differences drop below 0.001 threshold
- **Smart status updates** showing convergence progress
- **Visual feedback** with color-coded status indicators

### Dynamic Scaling
- **Auto-expanding y-axis** to accommodate all energy values
- **Responsive margins** (10% or minimum 0.1 Hartree buffer)
- **No cut-off lines** - complete convergence visibility

## 🎨 Technical Architecture

- **Framework**: Python Tkinter with Matplotlib integration
- **Data Generation**: Numpy-based exponential convergence algorithms
- **Real-time Updates**: Timer-based refresh with configurable intervals
- **UI Design**: Clean, modern interface with generous white spacing

## 📁 File Structure

```
John-Qubit/
├── vqe_simulator_dashboard.py    # Main application
├── requirements.txt              # Python dependencies
├── README.md                    # This file
└── .gitignore                   # Git ignore file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built for quantum computing enthusiasts and researchers
- Inspired by real VQE algorithms used in quantum chemistry
- Designed for educational and demonstration purposes

---

**John Qubit** - Making quantum simulation accessible and visual! 🌟
