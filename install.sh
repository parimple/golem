#!/bin/bash
# GOLEM Installation Script

echo "🚀 Installing GOLEM..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your DISCORD_TOKEN"
fi

echo "✅ Installation complete!"
echo ""
echo "To run GOLEM:"
echo "1. Edit .env file with your Discord bot token"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python run.py"