import PyPDF2

def split_pdf(input_pdf, output_pdf, start_page, end_page):
    # Open the input PDF file in read-binary mode
    with open(input_pdf, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)

        # Create a PDF writer object to write the extracted pages
        writer = PyPDF2.PdfWriter()

        # Loop through the range of pages (start_page to end_page)
        for page_num in range(start_page - 1, end_page):
            page = reader.pages[page_num]
            writer.add_page(page)

        # Write the output PDF file with the extracted pages
        with open(output_pdf, "wb") as output:
            writer.write(output)
        print(f"PDF split from page {start_page} to {end_page} saved as {output_pdf}.")

# Example usage:
# input_pdf_path = "./viettinbank-2024-01-13/vietinbank.pdf"
# output_pdf_path = "./viettinbank-2024-01-13/vietinbank-01.pdf"

# input_pdf_path = "/Users/nguyenthaichung/Desktop/Data/Github/Sao ke/mttq-sao-ke/dataset/2024-09-12/original/Agribank-1500201113838-20240901-20240912.pdf"
# output_pdf_path = "/Users/nguyenthaichung/Desktop/Data/Github/Sao ke/mttq-sao-ke/dataset/2024-09-12/original/Agribank-1500201113838-20240901-20240912-page12.pdf"

input_pdf_path = "/Users/nguyenthaichung/Desktop/Data/Github/Sao ke/mttq-sao-ke/dataset/2024-09-12/original/Vietinbank-111602391111-20240910-20240912.pdf"
output_pdf_path = "/Users/nguyenthaichung/Desktop/Data/Github/Sao ke/mttq-sao-ke/dataset/2024-09-12/original/Vietinbank-111602391111-20240910-20240912-page12.pdf"
start_page = 12  # Page 'a' (starting page, 1-based index)
end_page = 12    # Page 'b' (ending page, inclusive)

split_pdf(input_pdf_path, output_pdf_path, start_page, end_page)
