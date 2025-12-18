#!/bin/bash
# 设置数据库自动备份

SERVER_IP="150.107.38.113"
SERVER_USER="ubuntu"
SERVER_PASSWORD="15831929073asAS"
DEPLOY_DIR="/home/ubuntu/social-auto-upload"

echo "=========================================="
echo "设置数据库自动备份"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/ubuntu/social-auto-upload

echo "1️⃣ 创建备份目录..."
mkdir -p backups/database

echo "2️⃣ 创建备份脚本..."
cat > backup_database.sh << 'BACKUP_SCRIPT'
#!/bin/bash
# 数据库自动备份脚本

BACKUP_DIR="/home/ubuntu/social-auto-upload/backups/database"
DB_FILE="/home/ubuntu/social-auto-upload/db/database.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/database_backup_${TIMESTAMP}.db"

# 创建备份
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_FILE"
    echo "$(date): 数据库备份成功: $BACKUP_FILE" >> "${BACKUP_DIR}/backup.log"
    
    # 压缩备份（可选）
    gzip "$BACKUP_FILE"
    echo "$(date): 备份已压缩: ${BACKUP_FILE}.gz" >> "${BACKUP_DIR}/backup.log"
    
    # 只保留最近30天的备份
    find "$BACKUP_DIR" -name "database_backup_*.db.gz" -mtime +30 -delete
    
    echo "✅ 备份完成: ${BACKUP_FILE}.gz"
else
    echo "❌ 数据库文件不存在: $DB_FILE"
fi
BACKUP_SCRIPT

chmod +x backup_database.sh

echo "3️⃣ 立即执行一次备份..."
./backup_database.sh

echo ""
echo "4️⃣ 设置定时任务（每天凌晨2点备份）..."
(crontab -l 2>/dev/null | grep -v "backup_database.sh"; echo "0 2 * * * cd /home/ubuntu/social-auto-upload && ./backup_database.sh >> backups/database/backup.log 2>&1") | crontab -

echo "5️⃣ 查看当前定时任务..."
crontab -l

echo ""
echo "6️⃣ 列出已有备份..."
ls -lah backups/database/ | head -10

ENDSSH

echo ""
echo "=========================================="
echo "✅ 数据库备份设置完成！"
echo "=========================================="
echo "备份位置: /home/ubuntu/social-auto-upload/backups/database/"
echo "备份频率: 每天凌晨2点"
echo "保留时间: 30天"


