#!/bin/zsh

# Development startup script for life-as-a-garden project
# Starts backend, frontend, and rmapi-wrapper services in parallel

set -e

# Create a temporary shutdown signal file
SHUTDOWN_FILE="/tmp/dev-start-shutdown-$$"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[DEV-SCRIPT]${NC} $1"
}

print_error() {
    echo -e "${RED}[DEV-SCRIPT ERROR]${NC} $1"
}

print_service() {
    local service=$1
    local color=$2
    shift 2
    echo -e "${color}[$service]${NC} $*"
}

# Function to setup Python virtual environment and install dependencies
setup_python_service() {
    local service_name=$1
    local service_dir=$2
    local color=$3
    
    print_service "$service_name" $color "Setting up Python virtual environment..."
    
    if [[ ! -d ".venv" ]]; then
        print_service "$service_name" $color "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    if [[ ! -f "$service_dir/requirements.txt" ]]; then
        print_service "$service_name" $RED "requirements.txt not found in $service_dir"
        return 1
    fi
    
    print_service "$service_name" $color "Installing Python dependencies..."
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r "$service_dir/requirements.txt"
    
    print_service "$service_name" $color "Python setup complete"
}

# Function to setup Node.js dependencies
setup_node_service() {
    local service_name=$1
    local service_dir=$2
    local color=$3
    
    print_service "$service_name" $color "Setting up Node.js dependencies..."
    
    cd "$service_dir"
    
    if [[ ! -f "package.json" ]]; then
        print_service "$service_name" $RED "package.json not found in $service_dir"
        cd ..
        return 1
    fi
    
    print_service "$service_name" $color "Installing npm dependencies..."
    npm install
    
    print_service "$service_name" $color "Node.js setup complete"
    cd ..
}

# Function to cleanup background processes on exit
cleanup() {
    # Create shutdown signal file
    touch "$SHUTDOWN_FILE"
    print_status "Shutting down services..."
    
    # Kill all processes in the current process group
    if [[ -n "${BACKEND_PID:-}" ]]; then
        print_status "Stopping backend service..."
        kill -TERM -$BACKEND_PID 2>/dev/null || true
    fi
    
    if [[ -n "${FRONTEND_PID:-}" ]]; then
        print_status "Stopping frontend service..."
        kill -TERM -$FRONTEND_PID 2>/dev/null || true
    fi
    
    if [[ -n "${RMAPI_PID:-}" ]]; then
        print_status "Stopping rmapi-wrapper service..."
        kill -TERM -$RMAPI_PID 2>/dev/null || true
    fi
    
    # Kill any remaining FastAPI or Node processes on the specific ports
    print_status "Cleaning up any remaining processes..."
    
    # Kill processes on port 8000 (backend)
    local port_8000_pids=$(lsof -ti:8000 2>/dev/null || true)
    if [[ -n "$port_8000_pids" ]]; then
        for pid in $port_8000_pids; do
            kill -9 $pid 2>/dev/null || true
        done
    fi
    
    # Kill processes on port 8001 (rmapi-wrapper)
    local port_8001_pids=$(lsof -ti:8001 2>/dev/null || true)
    if [[ -n "$port_8001_pids" ]]; then
        for pid in $port_8001_pids; do
            kill -9 $pid 2>/dev/null || true
        done
    fi
    
    # Kill processes on port 5173 (frontend - Vite default)
    local port_5173_pids=$(lsof -ti:5173 2>/dev/null || true)
    if [[ -n "$port_5173_pids" ]]; then
        for pid in $port_5173_pids; do
            kill -9 $pid 2>/dev/null || true
        done
    fi
    
    # Kill any remaining background jobs
    local job_pids=$(jobs -p 2>/dev/null || true)
    if [[ -n "$job_pids" ]]; then
        for pid in $job_pids; do
            kill -TERM $pid 2>/dev/null || true
        done
    fi
    
    # Wait a moment for graceful shutdown
    sleep 1
    
    # Force kill any stubborn processes
    local job_pids_final=$(jobs -p 2>/dev/null || true)
    if [[ -n "$job_pids_final" ]]; then
        for pid in $job_pids_final; do
            kill -9 $pid 2>/dev/null || true
        done
    fi
    
    # Cleanup shutdown file
    rm -f "$SHUTDOWN_FILE"
    
    print_status "All services stopped."
    exit 0
}

# Trap signals to cleanup properly
trap cleanup SIGINT SIGTERM EXIT

# Check if required directories exist
if [[ ! -d "backend" ]]; then
    print_error "Backend directory not found!"
    exit 1
fi

if [[ ! -d "garden" ]]; then
    print_error "Garden (frontend) directory not found!"
    exit 1
fi

if [[ ! -d "rmapi-wrapper" ]]; then
    print_error "rmapi-wrapper directory not found!"
    exit 1
fi

print_status "Starting development environment..."

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    print_error "python3 not found. Please install Python 3."
    exit 1
fi

# Check if Node.js/npm is available
if ! command -v npm >/dev/null 2>&1; then
    print_error "npm not found. Please install Node.js and npm."
    exit 1
fi

print_status "Setting up dependencies..."

# Setup Python virtual environment and install backend dependencies
setup_python_service "SETUP" "backend" $CYAN
if [[ $? -ne 0 ]]; then
    print_error "Failed to setup backend dependencies"
    exit 1
fi

# Setup rmapi-wrapper dependencies (reusing the same .venv)
print_service "SETUP" $CYAN "Installing rmapi-wrapper dependencies..."
.venv/bin/pip install -r rmapi-wrapper/requirements.txt

# Setup frontend dependencies
setup_node_service "SETUP" "garden" $CYAN
if [[ $? -ne 0 ]]; then
    print_error "Failed to setup frontend dependencies"
    exit 1
fi

print_status "All dependencies installed successfully!"
print_status ""
print_status "Services will be available at:"
print_status "  Backend (FastAPI):     http://localhost:8000"
print_status "  Frontend (Vite):       http://localhost:5173"
print_status "  rmapi-wrapper:         http://localhost:8001"
print_status ""
print_status "Press Ctrl+C to stop all services"
print_status ""

# Start backend service
print_status "Starting backend service..."
(
    trap 'exit 0' TERM
    cd backend
    while [[ ! -f "$SHUTDOWN_FILE" ]]; do
        print_service "BACKEND" $BLUE "Starting FastAPI development server on port 8000..."
        if [[ -f "../.venv/bin/fastapi" ]]; then
            ../.venv/bin/fastapi dev main.py --port 8000 &
            local fastapi_pid=$!
            
            # Monitor both the fastapi process and shutdown signal
            while kill -0 $fastapi_pid 2>/dev/null && [[ ! -f "$SHUTDOWN_FILE" ]]; do
                sleep 1
            done
            
            # If shutdown signal exists, kill fastapi and exit
            if [[ -f "$SHUTDOWN_FILE" ]]; then
                kill $fastapi_pid 2>/dev/null || true
                exit 0
            fi
            
            # If we're here, fastapi crashed
            wait $fastapi_pid 2>/dev/null || true
        else
            print_service "BACKEND" $RED "fastapi not found in virtual environment"
            sleep 5
        fi
        
        [[ -f "$SHUTDOWN_FILE" ]] && exit 0
        print_service "BACKEND" $YELLOW "Backend service crashed. Restarting in 3 seconds..."
        sleep 3
    done
) &
BACKEND_PID=$!

# Start frontend service
print_status "Starting frontend service..."
(
    trap 'exit 0' TERM
    cd garden
    while [[ ! -f "$SHUTDOWN_FILE" ]]; do
        print_service "FRONTEND" $GREEN "Starting Vite development server..."
        if [[ -f "package.json" ]]; then
            npm run dev &
            local npm_pid=$!
            
            # Monitor both the npm process and shutdown signal
            while kill -0 $npm_pid 2>/dev/null && [[ ! -f "$SHUTDOWN_FILE" ]]; do
                sleep 1
            done
            
            # If shutdown signal exists, kill npm and exit
            if [[ -f "$SHUTDOWN_FILE" ]]; then
                kill $npm_pid 2>/dev/null || true
                exit 0
            fi
            
            # If we're here, npm crashed
            wait $npm_pid 2>/dev/null || true
        else
            print_service "FRONTEND" $RED "package.json not found in garden directory"
            sleep 5
        fi
        
        [[ -f "$SHUTDOWN_FILE" ]] && exit 0
        print_service "FRONTEND" $YELLOW "Frontend service crashed. Restarting in 3 seconds..."
        sleep 3
    done
) &
FRONTEND_PID=$!

# Start rmapi-wrapper service
print_status "Starting rmapi-wrapper service..."
(
    trap 'exit 0' TERM
    cd rmapi-wrapper
    while [[ ! -f "$SHUTDOWN_FILE" ]]; do
        print_service "RMAPI" $PURPLE "Starting rmapi-wrapper FastAPI server on port 8001..."
        if [[ -f "../.venv/bin/fastapi" ]]; then
            ../.venv/bin/fastapi dev main.py --port 8001 &
            local fastapi_pid=$!
            
            # Monitor both the fastapi process and shutdown signal
            while kill -0 $fastapi_pid 2>/dev/null && [[ ! -f "$SHUTDOWN_FILE" ]]; do
                sleep 1
            done
            
            # If shutdown signal exists, kill fastapi and exit
            if [[ -f "$SHUTDOWN_FILE" ]]; then
                kill $fastapi_pid 2>/dev/null || true
                exit 0
            fi
            
            # If we're here, fastapi crashed
            wait $fastapi_pid 2>/dev/null || true
        else
            print_service "RMAPI" $RED "fastapi not found in virtual environment"
            sleep 5
        fi
        
        [[ -f "$SHUTDOWN_FILE" ]] && exit 0
        print_service "RMAPI" $YELLOW "rmapi-wrapper service crashed. Restarting in 3 seconds..."
        sleep 3
    done
) &
RMAPI_PID=$!

# Wait for all background processes
wait $BACKEND_PID $FRONTEND_PID $RMAPI_PID
