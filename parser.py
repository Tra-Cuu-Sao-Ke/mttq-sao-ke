import argparse
import os
import sys
from abc import ABC, abstractmethod
from parser.AgribankParser import AgribankParser
from parser.BIDVParser import BIDVParser
from parser.VietcombankParser import VietcombankParser
from parser.VietinbankParser import VietinbankParser
from parser.BaseStatementParser import BaseStatementParser

# mttq-sao-ke/dataset/2024-09-10/original/Vietcombank-0011001932418-20240901-20240910.pdf
def get_parser_instance(bank, input_file, output_folder, structure, mode, fromOutputFileId):
    if bank == "Vietcombank":
        return VietcombankParser(input_file, output_folder, structure, mode, fromOutputFileId)
    elif bank == "Vietinbank":
        return VietinbankParser(input_file, output_folder, structure, mode, fromOutputFileId)
    elif bank == "BIDV":
        return BIDVParser(input_file, output_folder, structure, mode, fromOutputFileId)
    elif bank == "Agribank":
        return AgribankParser(input_file, output_folder, structure, mode, fromOutputFileId)
    else:
        raise ValueError("Unsupported bank")

def main():
    parser = argparse.ArgumentParser(description="Process bank statements.")
    parser.add_argument('bank', choices=['Vietcombank', 'Vietinbank', 'BIDV', 'Agribank'], 
                        help='The bank for which the statement is to be processed.')
    parser.add_argument('inputFilePath', type=str, 
                        help='Path to the input PDF file.')
    parser.add_argument('mode', choices=['textPdf', 'imagePdf'], 
                        help='The mode of processing: textPdf or imagePdf.')
    parser.add_argument('structure', choices=['tabular', 'paragraph'], 
                        help='The structure of the PDF content: tabular or paragraph.')
    parser.add_argument('outputFolderPath', nargs='?', default=None, 
                        help='Optional output folder path. If not specified, the default will be used.')

    # add optional arguments about the start transaction
    parser.add_argument('--fromOutputFileId', type=int, default=1, 
                        help='The start transaction index to process.')
    
    args = parser.parse_args()

    if args.outputFolderPath is None:
        input_folder = os.path.dirname(args.inputFilePath)
        args.outputFolderPath = os.path.join(os.path.dirname(input_folder), "output")
    else:
        # outputFolderPath must be a directory
        if not os.path.isdir(args.outputFolderPath):
            raise ValueError(f"outputFolderPath \"{args.outputFolderPath}\" must be a directory.")
        
    # print all arguments in a nice format
    print("#" * 50)
    print("* BANK STATEMENT PARSER *")
    for arg in vars(args):
        print(f"{arg}: {getattr(args, arg)}")
    print(f"output csv file path structure: {BaseStatementParser.get_output_file_path(args.inputFilePath, args.outputFolderPath, isSampleFilePath=True)}")
    print("#" * 50)
    print()

    parser_instance = get_parser_instance(args.bank, args.inputFilePath, args.outputFolderPath, args.structure, args.mode, args.fromOutputFileId)
    parser_instance.parse()

if __name__ == '__main__':
    main()