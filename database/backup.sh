#!/bin/bash

# MongoDB Backup Script for JoinUp
# Backs up the JoinUp database to a timestamped directory

# Configuration
DB_NAME="joinup"
BACKUP_DIR="/backup/joinup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"

# MongoDB connection (update if needed)
MONGO_HOST="localhost"
MONGO_PORT="27017"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "JoinUp Database Backup"
echo "=========================================="
echo ""

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "Backing up database: $DB_NAME"
echo "Backup location: $BACKUP_PATH"
echo ""

# Perform backup
mongodump --host $MONGO_HOST --port $MONGO_PORT --db $DB_NAME --out $BACKUP_PATH

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Backup completed successfully!${NC}"
    echo "Backup saved to: $BACKUP_PATH"
    
    # Compress backup
    echo ""
    echo "Compressing backup..."
    tar -czf "$BACKUP_PATH.tar.gz" -C $BACKUP_DIR $DATE
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Backup compressed${NC}"
        echo "Compressed file: $BACKUP_PATH.tar.gz"
        
        # Remove uncompressed backup
        rm -rf $BACKUP_PATH
        echo "Removed uncompressed files"
    fi
    
    # Delete backups older than 30 days
    echo ""
    echo "Cleaning up old backups (older than 30 days)..."
    find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +30 -delete
    echo -e "${GREEN}✓ Cleanup complete${NC}"
    
else
    echo ""
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "Backup Complete"
echo "=========================================="
