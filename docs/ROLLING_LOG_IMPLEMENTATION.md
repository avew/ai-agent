# Rolling Log Implementation

## Overview
The chat agent application now implements advanced rolling file logging with the following features:

- **Daily rotation**: Log files rotate at midnight every day
- **Size-based rotation**: Log files also rotate when they reach 100MB
- **Automatic compression**: Rotated log files are automatically compressed using gzip
- **Configurable retention**: Keeps a configurable number of days of log files (default: 30 days)

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENABLE_FILE_LOGGING` | `true` | Enable/disable file logging |
| `LOG_FILE` | `logs/app.log` | Path to the main log file |
| `LOG_BACKUP_COUNT` | `30` | Number of daily log files to keep |
| `LOG_FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format |

### Example .env Configuration

```env
# Logging Configuration
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
LOG_FILE=logs/app.log
LOG_BACKUP_COUNT=30
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## How It Works

### Daily Rotation
- Log files automatically rotate at midnight (00:00:00)
- New log file starts with the original name (e.g., `app.log`)
- Previous day's log is renamed with timestamp (e.g., `app.log.2025-06-11`)

### Size-Based Rotation
- If the current log file reaches 100MB before midnight, it triggers immediate rotation
- This prevents extremely large log files during high-traffic periods
- The rotated file gets a timestamp suffix

### Compression
- After rotation, the old log file is automatically compressed using gzip
- Compressed files have `.gz` extension (e.g., `app.log.2025-06-11.gz`)
- This significantly reduces disk space usage for archived logs

### Cleanup
- The system automatically removes old log files beyond the retention period
- Both compressed (.gz) and uncompressed files are considered for cleanup
- Default retention is 30 days (configurable via `LOG_BACKUP_COUNT`)

## File Naming Convention

```
logs/
├── app.log                      # Current active log file
├── app.log.2025-06-11.gz       # Yesterday's compressed log
├── app.log.2025-06-10.gz       # Day before yesterday's compressed log
├── app.log.2025-06-09.gz       # And so on...
└── ...
```

## Benefits

1. **Disk Space Efficiency**: Gzip compression typically reduces log file size by 80-90%
2. **Performance**: Daily rotation prevents single log files from becoming too large
3. **Reliability**: Size-based rotation ensures logs don't fill up disk space
4. **Maintenance**: Automatic cleanup removes old files without manual intervention
5. **Debugging**: Timestamped files make it easy to find logs from specific dates

## Implementation Details

### Custom Handler Class
The implementation uses a custom `CustomTimedRotatingFileHandler` class that extends Python's `TimedRotatingFileHandler` with:

- Size-based rotation capability
- Automatic gzip compression
- Enhanced file cleanup logic

### Rotation Triggers
Log rotation occurs when either condition is met:
1. **Time-based**: At midnight (daily rotation)
2. **Size-based**: When file size reaches 100MB

### Error Handling
- If compression fails, the original uncompressed file is kept
- Logging continues normally even if rotation encounters issues
- Warnings are logged for any compression failures

## Monitoring and Troubleshooting

### Check Current Log File Size
```bash
ls -lh logs/app.log
```

### View Compressed Log Files
```bash
ls -lh logs/*.gz
```

### Read Compressed Log Files
```bash
# View compressed log
zcat logs/app.log.2025-06-11.gz | tail -100

# Search in compressed logs
zgrep "ERROR" logs/app.log.2025-06-11.gz
```

### Verify Rotation is Working
1. Check that new files appear daily in the logs directory
2. Verify that old files are compressed (have .gz extension)
3. Confirm that files older than retention period are removed

## Customization

### Change Rotation Frequency
To rotate logs at different intervals, modify the `when` parameter in the handler configuration:

- `'H'`: Hourly
- `'D'`: Daily (default)
- `'W'`: Weekly
- `'midnight'`: Daily at midnight (current setting)

### Adjust File Size Limit
Modify the `maxBytes` parameter (currently set to 104857600 = 100MB):

```python
maxBytes=52428800,  # 50MB
maxBytes=209715200, # 200MB
```

### Change Retention Period
Adjust the `LOG_BACKUP_COUNT` environment variable:

```env
LOG_BACKUP_COUNT=7   # Keep only 7 days
LOG_BACKUP_COUNT=90  # Keep 90 days
```

## Testing

To test the rolling log functionality:

1. **Test Daily Rotation**: Temporarily change the rotation to hourly and wait
2. **Test Size Rotation**: Generate large amounts of log data to trigger size rotation
3. **Test Compression**: Verify that rotated files are properly compressed
4. **Test Cleanup**: Verify that old files are removed after retention period

```python
# Example: Generate test logs
import logging
logger = logging.getLogger('test')
for i in range(100000):
    logger.info(f"Test log message {i} with some additional content to increase file size")
```
