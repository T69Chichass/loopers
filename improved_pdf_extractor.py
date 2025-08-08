"""
Improved PDF text extraction with better handling of encoded/corrupted text.
"""
import fitz  # PyMuPDF
import pdfplumber
import re
from pathlib import Path

def extract_text_from_pdf_improved(file_path: Path) -> str:
    """
    Extract text from PDF with better error handling and text cleaning.
    """
    text_content = []
    
    try:
        # Method 1: Try pdfplumber first (better for complex layouts)
        print(f"🔍 Extracting text using pdfplumber...")
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    # Extract text
                    text = page.extract_text()
                    
                    if text and text.strip():
                        # Clean the extracted text
                        cleaned_text = clean_extracted_text(text)
                        if cleaned_text and len(cleaned_text) > 10:  # Only add meaningful text
                            text_content.append(f"[Page {page_num + 1}]\n{cleaned_text}")
                            print(f"   ✅ Page {page_num + 1}: {len(cleaned_text)} characters")
                        else:
                            print(f"   ⚠️ Page {page_num + 1}: Text too short or corrupted")
                    else:
                        print(f"   ❌ Page {page_num + 1}: No text found")
                        
                except Exception as e:
                    print(f"   ❌ Page {page_num + 1}: Error - {e}")
                    continue
        
        # Method 2: If pdfplumber fails, try PyMuPDF
        if not text_content:
            print(f"🔍 Trying PyMuPDF extraction...")
            doc = fitz.open(str(file_path))
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    if text and text.strip():
                        cleaned_text = clean_extracted_text(text)
                        if cleaned_text and len(cleaned_text) > 10:
                            text_content.append(f"[Page {page_num + 1}]\n{cleaned_text}")
                            print(f"   ✅ Page {page_num + 1}: {len(cleaned_text)} characters")
                        else:
                            print(f"   ⚠️ Page {page_num + 1}: Text too short or corrupted")
                    else:
                        print(f"   ❌ Page {page_num + 1}: No text found")
                        
                except Exception as e:
                    print(f"   ❌ Page {page_num + 1}: Error - {e}")
                    continue
            doc.close()
        
        # Method 3: Try extracting text blocks and images as fallback
        if not text_content:
            print(f"🔍 Trying text block extraction...")
            text_content = extract_text_blocks(file_path)
        
        return "\n\n".join(text_content) if text_content else ""
        
    except Exception as e:
        print(f"❌ All PDF extraction methods failed: {e}")
        return ""

def clean_extracted_text(text: str) -> str:
    """
    Clean and validate extracted text to remove corrupted/encoded content.
    """
    if not text:
        return ""
    
    # Remove non-printable characters but keep common symbols
    # Keep: letters, numbers, spaces, punctuation, common symbols
    printable_pattern = re.compile(r'[^\x20-\x7E\u00A0-\u024F\u1E00-\u1EFF\u2000-\u206F\u2070-\u209F\u20A0-\u20CF\u2100-\u214F\u2190-\u21FF\u2200-\u22FF]')
    text = printable_pattern.sub(' ', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove very short "words" that are likely encoding artifacts
    words = text.split()
    cleaned_words = []
    for word in words:
        # Keep words that are:
        # 1. At least 2 characters OR
        # 2. Single letters/numbers OR
        # 3. Common single-character words (a, I, etc.)
        if len(word) >= 2 or word.isalnum() or word.lower() in ['a', 'i', '&', '+', '-', '=']:
            cleaned_words.append(word)
    
    text = ' '.join(cleaned_words)
    
    # Check if the text looks like it's mostly corrupted
    # If more than 30% of characters are non-standard, it's likely corrupted
    if text:
        standard_chars = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,!?;:"()[]{}/-')
        corruption_ratio = 1 - (standard_chars / len(text))
        
        if corruption_ratio > 0.3:
            print(f"   ⚠️ Text appears corrupted (corruption ratio: {corruption_ratio:.2f})")
            return ""
    
    return text.strip()

def extract_text_blocks(file_path: Path) -> list:
    """
    Extract text using different methods to handle complex PDFs.
    """
    text_blocks = []
    
    try:
        doc = fitz.open(str(file_path))
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get text blocks (with better formatting)
            blocks = page.get_text("dict")
            page_text = []
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            line_text += span["text"]
                        if line_text.strip():
                            cleaned = clean_extracted_text(line_text)
                            if cleaned:
                                page_text.append(cleaned)
            
            if page_text:
                text_blocks.append(f"[Page {page_num + 1}]\n" + "\n".join(page_text))
        
        doc.close()
        return text_blocks
        
    except Exception as e:
        print(f"❌ Text block extraction failed: {e}")
        return []

def test_pdf_extraction():
    """Test the improved PDF extraction on the insurance policy."""
    pdf_path = Path("Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"🏥 Testing improved PDF extraction on: {pdf_path.name}")
    print("=" * 60)
    
    extracted_text = extract_text_from_pdf_improved(pdf_path)
    
    if extracted_text:
        print(f"\n✅ Extraction successful!")
        print(f"📊 Total extracted text length: {len(extracted_text)} characters")
        
        # Show first 500 characters to verify readability
        print(f"\n📝 First 500 characters:")
        print("-" * 40)
        print(extracted_text[:500])
        print("-" * 40)
        
        # Show some statistics
        lines = extracted_text.split('\n')
        words = extracted_text.split()
        print(f"\n📈 Statistics:")
        print(f"   Lines: {len(lines)}")
        print(f"   Words: {len(words)}")
        print(f"   Average word length: {sum(len(word) for word in words) / len(words):.1f}")
        
        # Check for common insurance terms
        insurance_terms = ['policy', 'premium', 'coverage', 'deductible', 'claim', 'benefit', 'medical', 'hospital']
        found_terms = [term for term in insurance_terms if term.lower() in extracted_text.lower()]
        print(f"   Insurance terms found: {', '.join(found_terms)}")
        
        return extracted_text
    else:
        print(f"\n❌ No readable text could be extracted")
        return None

if __name__ == "__main__":
    test_pdf_extraction()
