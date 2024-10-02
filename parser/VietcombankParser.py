import os
from abc import ABC, abstractmethod
from .BaseStatementParser import BaseStatementParser
import sys
import pdfplumber
import pandas as pd
import re

class VietcombankParser(BaseStatementParser):
  # static values 
  REGEXES = {
    "Date": r"^\d{2}\/\d{2}\/\d{4}$",
    "ReferenceNumber": r"^\d{4}\.\d{1,5}$",
    "CreditAmount": r"^[1-9](\d{0,2}(\.\d{3})*)$",
    # HH:MM:SS
    "Time": r"^\d{2}:\d{2}:\d{2}$"
  }

  DEFAULT_WIDTH_PIXEL = 2480
  DEFAULT_HEIGHT_PIXEL = 3509
  NUM_TRANSACTIONS_PER_FILE = 10000
  COLUMN_DIVIDERS_IN_PIXEL = [0, 424, 800, 1200, 1600, DEFAULT_WIDTH_PIXEL]

  def __init__(self, input_file, output_folder, structure, mode, fromOutputFileId: int):
    if structure != 'tabular':
      raise ValueError(f"Structure '{self.structure}' is not supported for Vietcombank. Only 'tabular' is supported.")
    
    super().__init__(input_file, output_folder, structure, mode, fromOutputFileId)

  # def findTransactionAnamolies(self):
  #   output_anamolies_file = BaseStatementParser.get_output_file_path(self.input_file, self.output_folder, custom_suffix="transaction_anamolies.csv")
  #   # traverse all rows
  #   rowsByDocNo = {}
  #   duplicatedDocNoSet = set()
  #   emptyDocNoSet = []
  #   for fileId in range(1, 10000):
  #     csv_file = self.to_csv_file_path(fileId)
  #     print(f"Traversing file {csv_file}")
  #     if not os.path.exists(csv_file):
  #       break
  #     df = pd.read_csv(csv_file)
  #     for index, row in df.iterrows():
  #       docNo = row['ReferenceNumber']
  #       if pd.isna(docNo):
  #         emptyDocNoSet.append(row)
  #       else:
  #         if docNo in rowsByDocNo:
  #           rowsByDocNo[docNo].append(row)
  #           duplicatedDocNoSet.add(docNo)
  #         else:
  #           rowsByDocNo[docNo] = [row]

  #   # write to output file
  #   if len(duplicatedDocNoSet) > 0:
  #     # ReferenceNumber, Date, PageId, TransactionDetails, Credit, Debit, Balance
  #     with open(output_anamolies_file, 'w') as f:
  #       f.write("ReferenceNumber, Date, PageId, TransactionDetails, Credit, Debit, Balance\n")
  #       for docNo in duplicatedDocNoSet:
  #         for row in rowsByDocNo[docNo]:
  #           f.write(f"{docNo}, {row['Date']}, {row['PageId']}, {row['TransactionDetails']}, {row['Credit']}, {row['Debit']}, {row['Balance']}\n")

  #       for row in emptyDocNoSet:
  #         f.write(f"EMPTY_DOC_NO, {row['Date']}, {row['PageId']}, {row['TransactionDetails']}, {row['Credit']}, {row['Debit']}, {row['Balance']}\n")  

  #     print(f"Found {len(duplicatedDocNoSet)} duplicated ReferenceNumber and {len(emptyDocNoSet)} empty ReferenceNumber. Check {output_anamolies_file}")

  def mapToCanonicalTransaction(self, row):
    return {
      "PageId": row["PageId"],
      "Date": row["Date"],
      "Time": row["Time"] if "Time" in row else "",
      "DocumentNumber": row["DocumentNumber"] if "DocumentNumber" in row else "",
      "ReferenceNumber": row["ReferenceNumber"] if "ReferenceNumber" in row else "",
      "TransactionDetails": row["TransactionDetails"],
      "DebitAmount": row["DebitAmount"] if "DebitAmount" in row else "",
      "CreditAmount": row["CreditAmount"] if "CreditAmount" in row else "",
      "Balance": row["Balance"] if "Balance" in row else "",
      "OffsetAccount": row["OffsetAccount"] if "OffsetAccount" in row else ""
    }

  def applyPatch(self, row):
    if self.patchData is None:
      return row

    for index, patchRow in self.patchData.iterrows():
      if row['PageId'] == patchRow['PageId'] and row['Date'] == patchRow['Date'] and row['ReferenceNumber'] == patchRow['ReferenceNumber']:
        return patchRow.to_dict()

    return row

  def textLocationBasedExtraction(self, page, numItemsInTheFirstColumn = 0):
    words = page.extract_words()

    footer = []
    endOfHeader = 'Name' # 'Ref.' 'no' -> usually the last header cell in the ONLY table in each page

    # cut from the first position of "Transactions"
    words = words[[word['text'] for word in words].index(endOfHeader) + 1:] # ignore the account statement info in the first page
    words = words[:-len(footer)] # ignore footer details

    # filter top position for all words that satisfy regex for Date
    isStartOfRows = {}
    sortedWords = sorted(enumerate(words), key=lambda word: (word[1]['x0'], word[1]['top']))[:numItemsInTheFirstColumn]
    # identify the tokens in the first column (leftmost tokens)
    sortedWords = sorted(sortedWords, key=lambda word: word[1]['top'])
    row_top_positions = []
    for (j, word) in sortedWords:
      if re.match(VietcombankParser.REGEXES["Date"], word['text'].strip()):
        row_top_positions.append(word)

    row_top_positions.append({
      'top': max([word['bottom'] for word in words])
    })

    foundRows = []
    for i in range(1, len(row_top_positions)):
      top = row_top_positions[i-1]['top']
      bottom = row_top_positions[i]['top']

      if(top >= bottom): # panic error
        raise Exception("invalid row")

      rowIdInPage = i - 1

      # find all words in the range of top & bottom
      wordsInRow = [word for word in words if word['top'] >= top and word['bottom'] <= bottom]

      rowData = []

      colDividers = VietcombankParser.COLUMN_DIVIDERS_IN_PIXEL
      for col in range(1, len(colDividers)):
        leftPixel = colDividers[col-1] + 3 # ignore the border
        rightPixel = colDividers[col] + 3 # ignore the border
        
        left = leftPixel / colDividers[-1] * page.width
        right = rightPixel / colDividers[-1] * page.width

        topPixel = top/page.height * VietcombankParser.DEFAULT_HEIGHT_PIXEL
        bottomPixel = bottom/page.height * VietcombankParser.DEFAULT_HEIGHT_PIXEL

        cellData = sorted([word for word in wordsInRow if word['x0'] >= left and not word['x0'] >= right], key=lambda word: (word['top'], word['x0']))
        rowData.append(' '.join([word['text'] for word in cellData]))
      
      print("new row data: ", rowData)
      # ['10/09/2024', 'ung ho cac tinh bi bao lu', '', '100,000', '7,774,700', '92947305']
      foundRows.append({
        "PageId": str(page.page_number), # page.page_number is already 1-based index
        "Date": rowData[0].strip(),
        "TransactionDetails": ' '.join(rowData[1].strip().split("\n")),
        "DebitAmount": rowData[2],
        "CreditAmount": rowData[3].replace(",","_").replace(".", ",").replace("_", "."),
        "Balance": rowData[4],
        "ReferenceNumber": rowData[5]
      })

    return foundRows

  def simpleTextBasedExtraction(self, page, numItemsInTheFirstColumn = 0):
    table = page.extract_table()[1:]

    foundRows = []
    for (rowIdInPage, rowData) in enumerate(table[1:]):
      if len([x for x in rowData if len(x.strip()) > 0]) <= 0: continue # invalid row
      newRow = {
        "PageId": str(page.page_number), # page.page_number is already 1-based index
        # "DocNo": rowData[0],
        "Date": rowData[1].split("\n")[0],
        "Time": rowData[1].split("\n")[1],
        "TransactionDetails": rowData[2],
        "DebitAmount": "",
        "CreditAmount": rowData[3].replace(",","_").replace(".", ",").replace("_", "."),
        "OffsetAccount": rowData[4]
      }

      foundRows.append(newRow)
    
    return foundRows

  def parseTextPdf(self):
    self.findTransactionAnamolies()
    sys.exit()

    print(f"Parsing Vietcombank text PDF file: {self.input_file}")
    (countPrevTransactions, lastPageId) = self.getFirst1BasedPositionsToParse()
    start_row_id = VietcombankParser.NUM_TRANSACTIONS_PER_FILE * (self.fromOutputFileId - 1) + 1

    print(f"Start from row {start_row_id} and page {lastPageId}")

    totalNumberOfTransactions = countPrevTransactions

    with pdfplumber.open(self.input_file) as pdf:
      allRows = [] # push to new csv file for each 10000 transactions
      originFileName = os.path.basename(self.input_file)
      fileId = self.fromOutputFileId - 1

      for pageId in range(lastPageId - 1, len(pdf.pages)):
        page = pdf.pages[pageId]
        if (pageId) % 100 == 0: print(f"Processing page {pageId + 1}/{len(pdf.pages)}")
        table = page.extract_table()[1:]
        if not table: continue
        #######################  
        numColumns = len(table)
        if totalNumberOfTransactions + numColumns < start_row_id:
          totalNumberOfTransactions += numColumns
          continue
        #######################  
        # foundRows = self.textLocationBasedExtraction(page, numItemsInTheFirstColumn = numColumns)
        foundRows = self.simpleTextBasedExtraction(page, numItemsInTheFirstColumn = numColumns)
        totalNumberOfTransactions += len(foundRows)
        allRows.extend(foundRows)

        for newRow in foundRows:
          try:
            assert self.validateCanonicalTransaction(self.applyPatch(self.formatPandaType(self.mapToCanonicalTransaction(newRow))))
          except ValueError:
            # First, Write this as an anamoly to log file
            self.logAnamoly(f"New anamoly: raw = {newRow}, formatted = {newRow}")
            newRow['Balance'] = "0"
            newRow['CreditAmount'] = "0"
            newRow['DebitAmount'] = "0"
            # Second, ask ChatGPT to derive the correct value of the anamolies (should give it example on how a transaction detail (invalid field) should be)
            # Third, update the patch file with the correct values and re-run the parser again

        while len(allRows) >= 10000:
          fileId += 1

          self.pushToCsvFile(allRows[:10000], fileId)
          allRows = allRows[10000:]
      
      if len(allRows) > 0:
        fileId += 1
        self.pushToCsvFile(allRows, fileId)

  def parseImagePdf(self):
    # VietcombankParser does not support imagePdf mode
    raise NotImplementedError("VietcombankParser does not support imagePdf mode.")




# import os
# from abc import ABC, abstractmethod
# from .BaseStatementParser import BaseStatementParser
# import sys
# import pdfplumber
# import pandas as pd
# import re

# class VietcombankParser(BaseStatementParser):
#   REGEXES = {
#     "TNXDate": r"^\d{2}\/\d{2}\/\d{4}$",
#     "DocNo": r"^\d{4}\.\d{1,5}$",
#     "Credit": r"^[1-9](\d{0,2}(\.\d{3})*)$"
#   }

#   DEFAULT_WIDTH_PIXEL = 2480
#   DEFAULT_HEIGHT_PIXEL = 3509
#   COLUMN_DIVIDERS_IN_PIXEL = [0, 424, 800, 1200, 1600, DEFAULT_WIDTH_PIXEL] # convert pdf to image and measure this
#   NUM_TRANSACTIONS_PER_FILE = 10000

#   def __init__(self, input_file, output_folder, structure, mode, fromOutputFileId: int):
#     if structure != 'tabular':
#       raise ValueError(f"Structure '{self.structure}' is not supported for Vietcombank. Only 'tabular' is supported.")
    
#     super().__init__(input_file, output_folder, structure, mode, fromOutputFileId)

#   def parseTextPdf(self):
#     print(f"Parsing Vietcombank text PDF file: {self.input_file}")
#     (countPrevTransactions, lastPageId) = self.getFirst1BasedPositionsToParse()
#     start_row_id = VietcombankParser.NUM_TRANSACTIONS_PER_FILE * (self.fromOutputFileId - 1) + 1

#     print(f"Start from row {start_row_id} and page {lastPageId}")

#     totalNumberOfTransactions = countPrevTransactions

#     with pdfplumber.open(self.input_file) as pdf:
#       allRows = [] # push to new csv file for each 10000 transactions
#       originFileName = os.path.basename(self.input_file)
#       fileId = self.fromOutputFileId - 1

#       for pageId in range(lastPageId - 1, len(pdf.pages)):
#         page = pdf.pages[pageId]
#         if (pageId) % 100 == 0: print(f"Processing page {pageId + 1}/{len(pdf.pages)}")
#         table = page.extract_table()[1:]
#         if not table: continue
#         table = table[0]
#         columns = [col.strip().split('\n') if col else "" for col in table]
#         firstColumn = [{ "Date": columns[0][i], "DocNo": columns[0][i + 1] } for i in range(0, len(columns[0]), 2)]

#         if len(columns[0]) % 2 != 0:
#           print("Found a wrong table in page ", pageId)
#           print("columns[0] = ", columns[0])
#           sys.exit()
        
#         numberOfRowsInPage = len(columns[0]) // 2
#         # print("There are ", numberOfRowsInPage, " transactions in page ", pageId)

#         words = page.extract_words()
#         # cut from the first position of "Transactions"
#         words = words[[word['text'] for word in words].index("Transactions"):] # ignore the account statement info in the first page
#         words = words[:-31] # ignore footer details

#         # filter top position for all words that satisfy regex for TNXDate
#         isStartOfRows = {}
#         sortedWords = sorted(enumerate(words), key=lambda word: (word[1]['x0'], word[1]['top']))[:len(firstColumn) * 2]
#         # identify the tokens in the first column (leftmost tokens)
#         sortedWords = sorted(sortedWords, key=lambda word: word[1]['top'])
#         row_top_positions = []
#         for (j, word) in sortedWords:
#           if re.match(VietcombankParser.REGEXES["TNXDate"], word['text'].strip()):
#             row_top_positions.append(word)

#         row_top_positions.append({
#           'top': max([word['bottom'] for word in words])
#         })

#         for i in range(1, len(row_top_positions)):
#           totalNumberOfTransactions += 1 # new transaction
#           if totalNumberOfTransactions == start_row_id:
#             allRows.clear() # start the first page being extracted

#           top = row_top_positions[i-1]['top']
#           bottom = row_top_positions[i]['top']

#           if(top >= bottom): # panic error
#             raise Exception("invalid row")

#           rowIdInPage = i - 1

#           # find all words in the range of top & bottom
#           wordsInRow = [word for word in words if word['top'] >= top and word['bottom'] <= bottom]

#           rowData = []

#           for col in range(1, len(VietcombankParser.COLUMN_DIVIDERS_IN_PIXEL)):
#             leftPixel = VietcombankParser.COLUMN_DIVIDERS_IN_PIXEL[col-1] + 3 # ignore the border
#             rightPixel = VietcombankParser.COLUMN_DIVIDERS_IN_PIXEL[col] - 3 # ignore the border
#             # scale to pdf width
#             left = leftPixel / VietcombankParser.COLUMN_DIVIDERS_IN_PIXEL[-1] * page.width
#             right = rightPixel / VietcombankParser.COLUMN_DIVIDERS_IN_PIXEL[-1] * page.width

#             topPixel = top/page.height * VietcombankParser.DEFAULT_HEIGHT_PIXEL
#             bottomPixel = bottom/page.height * VietcombankParser.DEFAULT_HEIGHT_PIXEL

#             rowData.append(sorted([word for word in wordsInRow if word['x0'] >= left and word['x1'] <= right], key=lambda word: (word['top'], word['x0'])))
#             # TODO: filter from right to left 

#           allRows.append({
#             "pageId": pageId, # 0-index
#             "rowData": rowData,
#             "rowIdInPage": i - 1 # 0-index
#           })

#           if len(rowData[0]) != 2: # first cell must contain Date and DocNo
#             print("Found a wrong row ", allRows[-1])
#             print("wordsInRow = ", wordsInRow)
#             sys.exit()

#           if len(allRows) >= VietcombankParser.NUM_TRANSACTIONS_PER_FILE:
#             refinedRows = []
#             fileId += 1
#             self.pushToCsvFile(allRows, fileId)
#             allRows.clear()
      
#       if len(allRows) > 0:
#         fileId += 1
#         self.pushToCsvFile(allRows, fileId)

#   def pushToCsvFile(self, rows: list, fileId: int):
#     refinedRows = []
#     csvFileName = self.to_csv_file_path(fileId)
#     for (j, curRow) in enumerate(rows):
#       curRowData = curRow['rowData']
#       curPageId = curRow['pageId']
#       cellTexts = [' '.join([word['text'] for word in col]) for col in curRowData[1:]]
#       try:
#         newRefinedRow = {
#           "PageId": str(curPageId + 1),
#           "TNXDate": curRowData[0][0]['text'],
#           "DocNo": curRowData[0][1]['text'],
#           "Debit": cellTexts[0],
#           "Credit": cellTexts[1],
#           "Balance": cellTexts[2],
#           "TransactionDetails": cellTexts[3]
#         }
#         refinedRows.append(newRefinedRow)
#       except IndexError:
#         print("Buggy at row ", curRow)
#         sys.exit() 

#     # append to csv
#     df = pd.DataFrame(refinedRows)
#     df.to_csv(csvFileName, mode='w+', header=True, index=False)

#     print(f"Write {len(rows)} transactions to ", csvFileName)
#     sys.exit()

#   def parseImagePdf(self):
#     # VietcombankParser does not support imagePdf mode
#     raise NotImplementedError("VietcombankParser does not support imagePdf mode.")
