# eod_config.py
"""
Configuration file for EOD functions and settings
"""

# EOD Function Configuration
EOD_FUNCTION_MAPPING = {
    'EOD_JOURNAL': {
        'name': 'ບັນທຶກ Journal ປະຈຳວັນ',
        'description': 'ເຄື່ອນຍ້າຍຂໍ້ມູນຈາກ ACTB_DAIRY_LOG ໄປ STTB_EOC_DAILY_LOG',
        'critical': True,  # If this fails, stop EOD process
        'timeout': 300,    # 5 minutes timeout
        'retry_count': 3
    },
    'EOD_BALANCE': {
        'name': 'ຄິດໄລ່ຍອດເງິນ',
        'description': 'ຄິດໄລ່ຍອດເງິນປະຈຳວັນ',
        'critical': True,
        'timeout': 600,    # 10 minutes timeout
        'retry_count': 3
    },
    'EOD_INTEREST': {
        'name': 'ຄິດໄລ່ດອກເບ້ຍ',
        'description': 'ຄິດໄລ່ດອກເບ້ຍຕ່າງໆ',
        'critical': True,
        'timeout': 900,    # 15 minutes timeout
        'retry_count': 2
    },
    'EOD_REPORT': {
        'name': 'ສ້າງລາຍງານ',
        'description': 'ສ້າງລາຍງານປະຈຳວັນ',
        'critical': False,  # Non-critical, continue even if fails
        'timeout': 1200,   # 20 minutes timeout
        'retry_count': 1
    },
    'EOD_BACKUP': {
        'name': 'ສຳຮອງຂໍ້ມູນ',
        'description': 'ສຳຮອງຂໍ້ມູນປະຈຳວັນ',
        'critical': False,
        'timeout': 1800,   # 30 minutes timeout
        'retry_count': 2
    },
    'EOD_NOTIFICATION': {
        'name': 'ສົ່ງແຈ້ງເຕືອນ',
        'description': 'ສົ່ງແຈ້ງເຕືອນການປິດບັນຊີສຳເລັດ',
        'critical': False,
        'timeout': 60,     # 1 minute timeout
        'retry_count': 1
    }
}

# EOD Process Settings
EOD_SETTINGS = {
    'max_total_runtime': 7200,  # 2 hours maximum for entire EOD process
    'log_detail_level': 'INFO', # DEBUG, INFO, WARNING, ERROR
    'auto_retry_failed': True,
    'send_notifications': True,
    'backup_before_start': False,
    'parallel_execution': False,  # Set to True to enable parallel execution of non-critical functions
}

# Status mappings
RECORD_STATUS_MAPPING = {
    'O': 'ເປີດ',
    'C': 'ປິດ',
    'D': 'ລຶບ'
}

AUTH_STATUS_MAPPING = {
    'A': 'ອະນຸມັດແລ້ວ',
    'U': 'ລໍຖ້າອະນຸມັດ',
    'R': 'ປະຕິເສດ'
}