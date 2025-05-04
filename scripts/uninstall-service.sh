#!/bin/bash

SERVICE_NAME="lmnop-transcribe.service"
SERVICE_FILE="$HOME/.config/systemd/user/$SERVICE_NAME"

echo "Attempting to uninstall $SERVICE_NAME..."

# Stop the service if it's running
echo "Stopping $SERVICE_NAME..."
systemctl --user stop $SERVICE_NAME || true

# Disable the service
echo "Disabling $SERVICE_NAME..."
systemctl --user disable $SERVICE_NAME || true

# Remove the service file
if [ -f "$SERVICE_FILE" ]; then
    echo "Removing $SERVICE_FILE..."
    rm "$SERVICE_FILE"
else
    echo "$SERVICE_FILE not found, skipping removal."
fi

# Reload systemd user configuration
echo "Reloading systemd user configuration..."
systemctl --user daemon-reload

echo "$SERVICE_NAME uninstallation complete (if it was installed)."
