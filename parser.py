import os
from pathlib import Path
import pymupdf

class PDFParser:
    """A class to parse PDF files into text format.
    
    This class handles the conversion of PDF documents to text files, managing both
    batch processing and individual file parsing.
    
    Attributes:
        input_dir: A Path object pointing to the directory containing PDF files.
        output_dir: A Path object pointing to the directory for output text files.
    """
    
    def __init__(self, input_dir, output_dir):
        """Initializes the PDFParser with input and output directories.
        
        Args:
            input_dir: String or Path to the directory containing PDF files.
            output_dir: String or Path to the directory for output text files.
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_all_pdfs(self):
        """Processes all PDF files in the input directory.
        
        Iterates through all PDF files in input_dir and converts each to text.
        """
        pdf_files = list(self.input_dir.glob('*.pdf'))
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            self._parse_single_pdf(pdf_file)
            
    def _parse_single_pdf(self, pdf_file):
        """Converts a single PDF file to text.
        
        Args:
            pdf_file: Path object pointing to the PDF file to be processed.
        """
        print(f"Processing: {pdf_file.name}")
        txt_file = self.output_dir / f"{pdf_file.stem}.txt"
        
        if txt_file.exists():
            print(f"{txt_file.name} already exists, skipping")
            return
            
        try:
            with pymupdf.open(pdf_file) as doc:
                text = '\n'.join(page.get_text() for page in doc)
                
                with open(txt_file, 'w', encoding='utf-8') as txt:
                    txt.write(text)
                    
                print(f"Saved to: {txt_file.name}")
                    
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")

if __name__ == "__main__":
    # 设置输入输出路径
    pdf_dir = "downloaded_papers"
    txt_dir = "parsed_papers" 
    
    parser = PDFParser(pdf_dir, txt_dir)
    parser.parse_all_pdfs()
