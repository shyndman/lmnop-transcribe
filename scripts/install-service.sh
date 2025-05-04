#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the directory of the script and change to it
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="lmnop-transcribe.service"
SERVICE_NAME="lmnop-transcribe.service"

echo "Creating systemd user service directory: $SERVICE_DIR"
mkdir -p "$SERVICE_DIR"

# Stop the service if it's running
if systemctl --user is-active --quiet "$SERVICE_NAME"; then
    echo "Stopping existing service: $SERVICE_NAME"
    systemctl --user stop "$SERVICE_NAME"
fi

echo "Copying service file to systemd user directory..."
cp ../res/$SERVICE_FILE "$SERVICE_DIR/"

echo "Reloading systemd manager configuration..."
systemctl --user daemon-reload

echo "Enabling the service to start on login..."
systemctl --user enable "$SERVICE_NAME"

echo "Starting the service immediately..."
systemctl --user start "$SERVICE_NAME"

echo "Service installation complete."
echo ""
echo "To check the service status, run:"
echo "systemctl --user status "$SERVICE_NAME""
