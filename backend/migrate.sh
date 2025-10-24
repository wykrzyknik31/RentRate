#!/bin/bash
# Database migration helper script for RentRate

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export FLASK_APP=app.py

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 {upgrade|migrate|current|history|downgrade}"
    echo ""
    echo "Commands:"
    echo "  upgrade    - Apply pending migrations to the database"
    echo "  migrate    - Generate a new migration from model changes"
    echo "  current    - Show current migration revision"
    echo "  history    - Show migration history"
    echo "  downgrade  - Revert the last migration"
    echo ""
    echo "Examples:"
    echo "  $0 upgrade              # Apply all pending migrations"
    echo "  $0 migrate              # Generate migration automatically"
    echo "  $0 current              # Check current database version"
}

if [ $# -eq 0 ]; then
    print_usage
    exit 1
fi

COMMAND=$1

case $COMMAND in
    upgrade)
        echo -e "${GREEN}Applying database migrations...${NC}"
        flask db upgrade
        echo -e "${GREEN}✓ Database upgraded successfully!${NC}"
        ;;
    migrate)
        if [ -n "$2" ]; then
            MESSAGE="$2"
        else
            echo -e "${YELLOW}Enter migration message:${NC}"
            read -r MESSAGE
        fi
        
        echo -e "${GREEN}Generating migration...${NC}"
        if [ -n "$MESSAGE" ]; then
            flask db migrate -m "$MESSAGE"
        else
            flask db migrate
        fi
        echo -e "${GREEN}✓ Migration generated successfully!${NC}"
        echo -e "${YELLOW}Remember to review the migration file before applying it.${NC}"
        ;;
    current)
        echo -e "${GREEN}Current database revision:${NC}"
        flask db current
        ;;
    history)
        echo -e "${GREEN}Migration history:${NC}"
        flask db history
        ;;
    downgrade)
        echo -e "${YELLOW}WARNING: This will revert the last migration!${NC}"
        echo -e "${YELLOW}Are you sure? (yes/no)${NC}"
        read -r CONFIRM
        if [ "$CONFIRM" = "yes" ]; then
            echo -e "${GREEN}Reverting last migration...${NC}"
            flask db downgrade
            echo -e "${GREEN}✓ Database downgraded successfully!${NC}"
        else
            echo -e "${RED}Operation cancelled.${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
