module.exports = {
  apps: [{
    name: 'sau-backend',
    script: 'sau_backend.py',
    interpreter: '/home/ubuntu/miniconda3/envs/social-auto-upload/bin/python3',
    env: {
      DISPLAY: ':99',
      PYTHONUNBUFFERED: '1'
    },
    error_file: './logs/backend-error.log',
    out_file: './logs/backend-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    merge_logs: true,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  }]
}
