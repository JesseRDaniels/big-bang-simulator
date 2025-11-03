#!/bin/bash
# Big Bang Simulator Launcher
# Run this script directly in your terminal to see the GUI

cd "$(dirname "$0")"
source venv/bin/activate
python src/simulation/simulator.py
