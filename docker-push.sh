#!/bin/bash

# Configuration
IMAGE_NAME="growlog"
TAG="latest"
REMOTE_USER="admin"
REMOTE_HOST="192.168.0.168"
REMOTE_DIR="/home/admin/server/growlog"

# Save the Docker image as a tar file
IMAGE_TAR="${IMAGE_NAME}_${TAG}.tar"
echo "Saving Docker image to ${IMAGE_TAR}..."
docker save -o "${IMAGE_TAR}" "${IMAGE_NAME}:${TAG}"

# Transfer the image to the remote server
echo "Transferring image to ${REMOTE_HOST}..."
scp "${IMAGE_TAR}" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

if [ $? -ne 0 ]; then
  echo "File transfer failed. Exiting."
  exit 1
fi

# Load the image on the remote server
echo "Loading image on remote server..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker load -i ${REMOTE_DIR}/${IMAGE_TAR} && rm ${REMOTE_DIR}/${IMAGE_TAR}"

if [ $? -eq 0 ]; then
  echo "Docker image successfully transferred and loaded on ${REMOTE_HOST}."
else
  echo "Failed to load Docker image on ${REMOTE_HOST}."
  exit 1
fi

# Cleanup local tar file
rm -f "${IMAGE_TAR}"
echo "Cleanup complete."
