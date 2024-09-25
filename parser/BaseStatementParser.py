import os
from abc import ABC, abstractmethod
import pandas as pd
import re
import sys

class BaseStatementParser(ABC):
    REGEXES = {

        # "PageId",
        # "Date",
        # "DocumentNumber",
        # "ReferenceNumber",
        # "TransactionDetails",
        # "DebitAmount", # 000,000,000.00
        # "CreditAmount",
        # "Balance", # 000,000,000.00
        # "OffsetAccount"
      "PageId": r"^\d{1,5}$",
      "Date": r"^\d{2}\/\d{2}\/\d{4}$",
      "Time": r"^\d{2}:\d{2}:\d{2}$", 
      "MoneyAmount": r"^(\d{1,3}(,\d{3})*)(\.\d{3}(,\d{3})*){0,1}$" # 123,456,789.123,456
    }
    TRANSACTION_PANDA_TYPE = {
      "PageId": int,
      "Date": str,
      "Time": str,
      "DocumentNumber": str,
      "ReferenceNumber": str,
      "TransactionDetails": str,
      "DebitAmount": str,
      "CreditAmount": str,
      "Balance": str,
      "OffsetAccount": str
    }

    def __init__(self, input_file, output_folder, structure, mode, fromOutputFileId:int):
        # Validate input_file
        if not input_file.lower().endswith('.pdf'):
            raise ValueError(f"inputFilePath '{input_file}' must be a PDF bank statement file.")
        self.input_file = input_file

        # Validate output_folder
        if not os.path.isdir(os.path.dirname(output_folder)):
          self.output_folder = os.path.dirname(os.path.dirname(input_file)) + '/output'
        else: self.output_folder = output_folder

        # Validate structure
        if structure not in ['tabular', 'paragraph']:
            raise ValueError(f"Structure '{structure}' is not supported. Only 'tabular' and 'paragraph' are supported.")
        self.structure = structure

        # Validate mode
        if mode not in ['textPdf', 'imagePdf']:
            raise ValueError(f"Mode '{mode}' is not supported. Only 'textPdf' and 'imagePdf' are supported.")
        self.mode = mode

        if fromOutputFileId < 1:
            raise ValueError(f"fromOutputFileId '{fromOutputFileId}' must be a positive integer")
        self.fromOutputFileId = fromOutputFileId

        self.patchFilePath = os.path.dirname(input_file) + '/' + os.path.splitext(os.path.basename(input_file))[0]+"_patch.csv"
        self.logFilePath = os.path.dirname(input_file) + '/' + os.path.splitext(os.path.basename(input_file))[0]+"_log.txt"
        open(self.logFilePath, 'w').close()

        try:
          with open(self.patchFilePath, 'r') as f:
            # specify type for each column when reading csv
            self.patchData = pd.read_csv(f, keep_default_na=False).astype(BaseStatementParser.TRANSACTION_PANDA_TYPE)

            # validate each row 
            for index, row in self.patchData.iterrows():
              if not self.validateCanonicalTransaction(row.to_dict()):
                raise ValueError(f"Row {index} in the patch file {self.patchFilePath} is invalid.")
          print("Found valid patch file: ", self.patchFilePath)
          print(self.patchData)

        except FileNotFoundError:
          self.patchData = None
    
    def logAnamoly(self, message):
      with open(self.logFilePath, 'a') as f:
        f.write(message + '\n')
    
    def parse(self):
        if self.mode == 'textPdf':
            print(f"Parsing text PDF file: {self.input_file}")
            self.parseTextPdf()
        elif self.mode == 'imagePdf':
            print(f"Parsing image PDF file: {self.input_file}")
            self.parseImagePdf()
        pass

    def getFirst1BasedPositionsToParse(self): # 1-based index
      NUM_TRANSACTIONS_PER_FILE = 10000
      countPrevTransactionsNotIncludingLastPage = 0
      lastPageId = 1

      countEncounteredTransactionsInLastPage = 0
      for i in range(1, self.fromOutputFileId):
        csv_file = self.to_csv_file_path(i)
        if not os.path.exists(csv_file):
          sys.exit(f"File {csv_file} does not exist.")
        df = pd.read_csv(csv_file)

        if len(df) != NUM_TRANSACTIONS_PER_FILE:
          sys.exit(f"File {csv_file} does not have exactly {NUM_TRANSACTIONS_PER_FILE} transactions.")
        
        countPrevTransactionsNotIncludingLastPage += len(df)
        lastPageId = df.tail(1)['PageId'].values[0]

        # filter out txs in the last page
        countEncounteredTransactionsInLastPage = len(df[df['PageId'] == lastPageId])
      
      countPrevTransactionsNotIncludingLastPage -= countEncounteredTransactionsInLastPage
      
      return (countPrevTransactionsNotIncludingLastPage, lastPageId)

    @abstractmethod
    def textLocationBasedExtraction(self, page, numItemsInTheFirstColumn = 0):
      pass

    @abstractmethod
    def simpleTextBasedExtraction(self, page, numItemsInTheFirstColumn = 0):
      pass
    
    def getCanonicalTransactionFields(self):
      return [
        "PageId",
        "Date",
        "Time",
        "DocumentNumber",
        "ReferenceNumber",
        "TransactionDetails",
        "DebitAmount", # 000,000,000.00
        "CreditAmount",
        "Balance", # 000,000,000.00
        "OffsetAccount"
      ]

    @abstractmethod
    def applyPatch(self, row):
      pass
    
    def validateCanonicalTransaction(self, row) -> bool: # row is dictionary
      REGEXES = BaseStatementParser.REGEXES
      canonicalTransactionFields = self.getCanonicalTransactionFields()
      # convert row to TRANSACTION_PANDA_TYPE

      try:
        for field in canonicalTransactionFields:
          if field not in row:
            raise ValueError(f"Field '{field}' is missing in the transaction {row}.")
        
        for field in row:
          if field not in canonicalTransactionFields:
            raise ValueError(f"Field '{field}' is not a valid field in the transaction {row}.")
        
        # add regexes to validate fields
        # get type of PageId
        if row['PageId'] < 1:
          raise ValueError(f"PageId '{row['PageId']}' is invalid.")
        
        if not re.match(REGEXES['Date'], row['Date']):
          raise ValueError(f"Date '{row['Date']}' is invalid.")
        
        if row["Time"] and not re.match(REGEXES['Time'], row['Time']):
          raise ValueError(f"Time '{row['Time']}' is invalid.")
        
        if row['DebitAmount'] and not re.match(REGEXES['MoneyAmount'], row['DebitAmount']):
          raise ValueError(f"DebitAmount '{row['DebitAmount']}' is invalid.")
        
        if row['CreditAmount'] and not re.match(REGEXES['MoneyAmount'], row['CreditAmount']):
          raise ValueError(f"CreditAmount '{row['CreditAmount']}' is invalid.")
        
        if row['Balance'] and not re.match(REGEXES['MoneyAmount'], row['Balance']):
          raise ValueError(f"Balance '{row['Balance']}' is invalid.")
      except ValueError as e:
        print(e)
        print("Invalid transaction: ", row)
        raise e
      
      # TODO: add missing validations
      return True

    def formatPandaType(self, row):
      for field in row:
        if field in BaseStatementParser.TRANSACTION_PANDA_TYPE:
          row[field] = BaseStatementParser.TRANSACTION_PANDA_TYPE[field](row[field])
      return row
    
    def pushToCsvFile(self, rows: list, fileId: int):
      csvFileName = self.to_csv_file_path(fileId)
      patchedRows = [self.applyPatch(self.formatPandaType(self.mapToCanonicalTransaction(row))) for row in rows]

      df = pd.DataFrame([row for row in patchedRows if self.validateCanonicalTransaction(row)])[self.getCanonicalTransactionFields()]
      df.to_csv(csvFileName, mode='w+', header=True, index=False)
      print(f"Write {len(rows)} transactions to ", csvFileName)

    @abstractmethod
    def mapToCanonicalTransaction(self, row):
      pass

    @abstractmethod
    def parseTextPdf(self):
        pass

    @abstractmethod
    def parseImagePdf(self):
        pass
    
    @staticmethod
    def get_output_file_path(input_file_path: str, output_folder_path: str, fileId: int = 0, isSampleFilePath: bool = False, custom_suffix: str = ''):
        # make sure fileId is padded with zeros
        fileIdStr = str(fileId).zfill(3)
        if isSampleFilePath:
          # represent digit as symbol
          fileIdStr = 'X' * len(fileIdStr)

        suffix = custom_suffix if len(custom_suffix) > 0 else f"parsed_{fileIdStr}.csv"
        base_name = os.path.basename(input_file_path)
        name, _ = os.path.splitext(base_name)
        return os.path.join(output_folder_path, f"{name}_{suffix}")

    def to_csv_file_path(self, fileId: int, isSampleFilePath: bool = False):
        return BaseStatementParser.get_output_file_path(self.input_file, self.output_folder, fileId, isSampleFilePath)