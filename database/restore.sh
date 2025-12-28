#!/bin/bash

# MongoDB Restore Script for JoinUp
# Restores the JoinUp database from a backup

# Configuration
DB_NAME="joinup"
BACKUP_DIR="/backup/joinup"

# MongoDB connection (update if needed)
MONGO_HOST="localhost"
MONGO_PORT="27017"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "JoinUp Database Restore"
echo "=========================================="
echo ""

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Available backups:"
    ls -lh $BACKUP_DIR/*.tar.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 $BACKUP_DIR/20250101_120000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}✗ Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will replace all data in the '$DB_NAME' database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo "Extracting backup..."
TEMP_DIR="/tmp/joinup_restore_$$"
mkdir -p $TEMP_DIR
tar -xzf "$BACKUP_FILE" -C $TEMP_DIR

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to extract backup${NC}"
    rm -rf $TEMP_DIR
    exit 1
fi

echo -e "${GREEN}✓ Backup extracted${NC}"

# Find the backup directory (should be a timestamp folder)
BACKUP_DATA=$(find $TEMP_DIR -type d -name "$DB_NAME" | head -1)

if [ -z "$BACKUP_DATA" ]; then
    echo -e "${RED}✗ Backup data not found in archive${NC}"
    rm -rf $TEMP_DIR
    exit 1
fi

echo ""
echo "Restoring database..."
mongorestore --host $MONGO_HOST --port $MONGO_PORT --db $DB_NAME --drop $BACKUP_DATA

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Database restored successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Restore failed!${NC}"
    rm -rf $TEMP_DIR
    exit 1
fi

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo "=========================================="
echo "Restore Complete"
echo "=========================================="
