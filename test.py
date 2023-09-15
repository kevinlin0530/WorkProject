import logging


# 設定日誌的基本配置
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 創建 FileHandler，將日誌寫入到 log.txt 檔案中
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(logging.INFO)

# 設定 FileHandler 的日誌格式
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 將 FileHandler 添加到日誌處理器
logging.getLogger().addHandler(file_handler)

def main():
    logging.debug('這是一個 DEBUG 級別的日誌訊息')
    logging.info('這是一個 INFO 級別的日誌訊息')
    logging.warning('這是一個 WARNING 級別的日誌訊息')
    logging.error('這是一個 ERROR 級別的日誌訊息')
    logging.critical('這是一個 CRITICAL 級別的日誌訊息')

if __name__ == "__main__":
    main()