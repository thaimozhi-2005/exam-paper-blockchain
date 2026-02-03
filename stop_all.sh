#!/bin/bash
echo "Stopping all services (Blockchain, Backend, Frontend)..."
lsof -ti:5000,8000,8545 | xargs -r kill -9
echo "Done! All services have been stopped."
