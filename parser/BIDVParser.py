import os
from abc import ABC, abstractmethod
from .BaseStatementParser import BaseStatementParser

class BIDVParser(BaseStatementParser):
    def parseTextPdf(self):
        # Implement parsing logic for BIDV in text PDF mode
        print(f"Parsing BIDV text PDF file: {self.input_file}")
        output_file = self.get_output_file_name(1)  # Example fileId
        print(f"Output will be saved to: {output_file}")

    def parseImagePdf(self):
        # BIDVParser does not support imagePdf mode
        raise NotImplementedError("BIDVParser does not support imagePdf mode.")
