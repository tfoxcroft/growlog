#!/bin/bash

# Build the Docker image
docker build -t growlog .

echo "Docker image built successfully. To run:"
echo "docker run -p 5000:5000 growlog"