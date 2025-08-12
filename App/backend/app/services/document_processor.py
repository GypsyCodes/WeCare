"""
Document processing service with advanced OCR and NLP
"""
import os
import time
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
from celery import current_task
import spacy
from spacy.matcher import Matcher

from app.services.celery_app import celery_app
from app.core.config import settings

# Load Portuguese language model for NLP
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    # Fallback to English if Portuguese not available
    nlp = spacy.load("en_core_web_sm")

def enhance_image_quality(image_path: str) -> np.ndarray:
    """Enhance image quality for better OCR results"""
    # Read image
    image = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    
    # Apply adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def preprocess_image_for_ocr(image_path: str) -> np.ndarray:
    """Advanced preprocessing for OCR"""
    # Read image
    image = cv2.imread(image_path)
    
    # Resize if too small
    height, width = image.shape[:2]
    if width < 800:
        scale = 800 / width
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply noise reduction
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Apply bilateral filter to preserve edges
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def extract_text_with_multiple_methods(image_path: str) -> Dict[str, str]:
    """Extract text using multiple OCR methods for better accuracy"""
    results = {}
    
    try:
        # Method 1: Standard preprocessing
        processed1 = preprocess_image_for_ocr(image_path)
        config1 = '--oem 3 --psm 6 -l por'
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
        
        text1 = pytesseract.image_to_string(processed1, config=config1)
        results['standard'] = text1.strip()
        
        # Method 2: Enhanced preprocessing
        processed2 = enhance_image_quality(image_path)
        text2 = pytesseract.image_to_string(processed2, config=config1)
        results['enhanced'] = text2.strip()
        
        # Method 3: Different PSM modes
        config3 = '--oem 3 --psm 3 -l por'  # Fully automatic page segmentation
        text3 = pytesseract.image_to_string(processed1, config=config3)
        results['auto_segmentation'] = text3.strip()
        
        # Method 4: With confidence scores
        data = pytesseract.image_to_data(processed1, config=config1, output_type=pytesseract.Output.DICT)
        high_confidence_text = []
        for i, conf in enumerate(data['conf']):
            if conf > 60:  # Only text with confidence > 60%
                high_confidence_text.append(data['text'][i])
        results['high_confidence'] = ' '.join(high_confidence_text)
        
    except Exception as e:
        print(f"Error in OCR processing: {e}")
        results['error'] = str(e)
    
    return results

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using best OCR method"""
    try:
        # Try multiple methods
        results = extract_text_with_multiple_methods(image_path)
        
        # Choose the best result based on length and content
        best_text = ""
        best_score = 0
        
        for method, text in results.items():
            if method == 'error':
                continue
            
            # Score based on text length and presence of common words
            score = len(text)
            common_words = ['nome', 'cpf', 'rg', 'data', 'nascimento', 'endereço', 'telefone']
            for word in common_words:
                if word.lower() in text.lower():
                    score += 10
            
            if score > best_score:
                best_score = score
                best_text = text
        
        return best_text if best_text else results.get('standard', '')
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using advanced methods"""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Method 1: Direct text extraction
            page_text = page.get_text()
            
            if page_text.strip():
                all_text.append(page_text)
            else:
                # Method 2: OCR for scanned pages
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
                img_data = pix.tobytes("png")
                
                # Save temporary image
                temp_img_path = f"/tmp/temp_page_{page_num}_{int(time.time())}.png"
                with open(temp_img_path, "wb") as f:
                    f.write(img_data)
                
                # Extract text from image
                ocr_text = extract_text_from_image(temp_img_path)
                all_text.append(ocr_text)
                
                # Clean up temp file
                if os.path.exists(temp_img_path):
                    os.unlink(temp_img_path)
        
        doc.close()
        return "\n".join(all_text).strip()
        
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_cpf(text: str) -> Optional[str]:
    """Extract CPF from text using advanced regex"""
    # Multiple CPF patterns
    patterns = [
        r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',  # Standard format
        r'\b\d{11}\b',  # Numbers only
        r'CPF[:\s]*(\d{3}\.?\d{3}\.?\d{3}-?\d{2})',  # With CPF label
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean and validate
            cpf = re.sub(r'[^\d]', '', match)
            if len(cpf) == 11 and validate_cpf(cpf):
                return format_cpf(cpf)
    
    return None

def validate_cpf(cpf: str) -> bool:
    """Validate CPF using algorithm"""
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Calculate first digit
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = (sum1 * 10) % 11
    if digit1 == 10:
        digit1 = 0
    
    # Calculate second digit
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = (sum2 * 10) % 11
    if digit2 == 10:
        digit2 = 0
    
    return int(cpf[9]) == digit1 and int(cpf[10]) == digit2

def format_cpf(cpf: str) -> str:
    """Format CPF with dots and dash"""
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def extract_rg(text: str) -> Optional[str]:
    """Extract RG from text"""
    patterns = [
        r'RG[:\s]*(\d{1,2}\.?\d{3}\.?\d{3}-?\d{1})',
        r'\b\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}\b',
        r'Registro Geral[:\s]*(\d{1,2}\.?\d{3}\.?\d{3}-?\d{1})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_cnes(text: str) -> Optional[str]:
    """Extract CNES from text"""
    patterns = [
        r'CNES[:\s]*(\d{7})',
        r'\b\d{7}\b',  # 7 digits
        r'Cadastro Nacional[:\s]*(\d{7})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_coren(text: str) -> Optional[str]:
    """Extract COREN from text"""
    patterns = [
        r'COREN[:\s]*(\d{6})',
        r'\b\d{6}\b',  # 6 digits
        r'Conselho Regional[:\s]*(\d{6})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_data_nascimento(text: str) -> Optional[str]:
    """Extract birth date from text"""
    patterns = [
        r'Data de Nascimento[:\s]*(\d{1,2}/\d{1,2}/\d{4})',
        r'Nascimento[:\s]*(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{1,2}-\d{1,2}-\d{4})',
        r'(\d{4}-\d{1,2}-\d{1,2})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Try to parse and validate date
                date_str = matches[0]
                if '/' in date_str:
                    day, month, year = date_str.split('/')
                elif '-' in date_str:
                    parts = date_str.split('-')
                    if len(parts[0]) == 4:  # YYYY-MM-DD
                        year, month, day = parts
                    else:  # DD-MM-YYYY
                        day, month, year = parts
                
                # Validate date
                if 1900 <= int(year) <= datetime.now().year:
                    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            except:
                continue
    
    return None

def extract_nome(text: str) -> Optional[str]:
    """Extract name from text using NLP"""
    try:
        doc = nlp(text)
        
        # Look for name patterns
        name_patterns = [
            [{"POS": "PROPN"}, {"POS": "PROPN"}],  # Two proper nouns
            [{"LOWER": "nome"}, {"IS_TITLE": True}, {"IS_TITLE": True}],
            [{"LOWER": "nome"}, {"POS": "PROPN"}, {"POS": "PROPN"}],
        ]
        
        matcher = Matcher(nlp.vocab)
        for pattern in name_patterns:
            matcher.add("NAME", [pattern])
        
        matches = matcher(doc)
        for match_id, start, end in matches:
            name = doc[start:end].text
            if len(name.split()) >= 2:  # At least first and last name
                return name.title()
        
        # Fallback: look for common name patterns
        lines = text.split('\n')
        for line in lines:
            if 'nome' in line.lower():
                # Extract text after "nome"
                parts = line.split(':')
                if len(parts) > 1:
                    name = parts[1].strip()
                    if len(name.split()) >= 2:
                        return name.title()
        
    except Exception as e:
        print(f"Error extracting name: {e}")
    
    return None

def extract_endereco(text: str) -> Optional[str]:
    """Extract address from text"""
    patterns = [
        r'Endereço[:\s]*(.+?)(?:\n|$)',
        r'Endereço[:\s]*(.+?)(?:CEP|Telefone|Email)',
        r'Rua[:\s]*(.+?)(?:\n|$)',
        r'Av[:\s]*(.+?)(?:\n|$)',
        r'Avenida[:\s]*(.+?)(?:\n|$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            address = matches[0].strip()
            if len(address) > 10:  # Minimum address length
                return address
    
    return None

def extract_telefone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    patterns = [
        r'Telefone[:\s]*(\d{2}\s?\d{4,5}-?\d{4})',
        r'Tel[:\s]*(\d{2}\s?\d{4,5}-?\d{4})',
        r'(\d{2}\s?\d{4,5}-?\d{4})',
        r'(\d{2}\s?\d{8,9})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_email(text: str) -> Optional[str]:
    """Extract email from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def analyze_document_quality(text: str) -> Dict[str, Any]:
    """Analyze document quality and confidence"""
    analysis = {
        'text_length': len(text),
        'word_count': len(text.split()),
        'confidence_score': 0,
        'quality_indicators': [],
        'issues': []
    }
    
    # Calculate confidence based on various factors
    confidence = 0
    
    # Text length factor
    if len(text) > 100:
        confidence += 20
    elif len(text) > 50:
        confidence += 10
    
    # Presence of key information
    key_fields = ['cpf', 'rg', 'nome', 'data', 'endereço', 'telefone']
    found_fields = 0
    for field in key_fields:
        if field.lower() in text.lower():
            found_fields += 1
            confidence += 10
    
    analysis['found_fields'] = found_fields
    
    # Check for common OCR issues
    if '|' in text or 'l' in text and 'I' in text:
        analysis['issues'].append('Character recognition issues')
        confidence -= 10
    
    if len(text.split()) < 10:
        analysis['issues'].append('Very short text')
        confidence -= 20
    
    # Quality indicators
    if found_fields >= 3:
        analysis['quality_indicators'].append('Good field coverage')
    
    if len(text) > 200:
        analysis['quality_indicators'].append('Sufficient text length')
    
    analysis['confidence_score'] = max(0, min(100, confidence))
    
    return analysis

def process_document_data(text: str, document_type: str) -> Dict[str, Any]:
    """Process document data and extract structured information"""
    extracted_data = {
        'cpf': extract_cpf(text),
        'rg': extract_rg(text),
        'nome': extract_nome(text),
        'data_nascimento': extract_data_nascimento(text),
        'endereco': extract_endereco(text),
        'telefone': extract_telefone(text),
        'email': extract_email(text),
        'document_type': document_type,
        'extraction_timestamp': datetime.now().isoformat(),
    }
    
    # Add type-specific extractions
    if document_type.lower() == 'coren':
        extracted_data['coren'] = extract_coren(text)
    elif document_type.lower() == 'cnes':
        extracted_data['cnes'] = extract_cnes(text)
    
    # Analyze document quality
    quality_analysis = analyze_document_quality(text)
    extracted_data['quality_analysis'] = quality_analysis
    
    return extracted_data

@celery_app.task(bind=True, name="app.services.document_processor.process_document_task")
def process_document_task(self, document_id: int):
    """Celery task to process document asynchronously"""
    from app.core.database import get_db
    from app.core.models import Documento
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    
    async def _process():
        async for db in get_db():
            try:
                # Get document
                query = select(Documento).where(Documento.id == document_id)
                result = await db.execute(query)
                document = result.scalar_one_or_none()
                
                if not document:
                    raise Exception(f"Document {document_id} not found")
                
                # Update task status
                self.update_state(
                    state='PROGRESS',
                    meta={'current': 10, 'total': 100, 'status': 'Reading document...'}
                )
                
                # Extract text based on file type
                file_path = document.arquivo_path
                if not os.path.exists(file_path):
                    raise Exception(f"File not found: {file_path}")
                
                if file_path.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                else:
                    text = extract_text_from_image(file_path)
                
                self.update_state(
                    state='PROGRESS',
                    meta={'current': 50, 'total': 100, 'status': 'Processing extracted text...'}
                )
                
                # Process extracted data
                extracted_data = process_document_data(text, document.tipo_documento)
                
                self.update_state(
                    state='PROGRESS',
                    meta={'current': 80, 'total': 100, 'status': 'Saving results...'}
                )
                
                # Update document with extracted data
                document.dados_extraidos = extracted_data
                document.processado = True
                document.data_processamento = datetime.now()
                
                await db.commit()
                
                self.update_state(
                    state='SUCCESS',
                    meta={
                        'current': 100,
                        'total': 100,
                        'status': 'Document processed successfully',
                        'result': {
                            'document_id': document_id,
                            'extracted_fields': len([k for k, v in extracted_data.items() if v and k not in ['document_type', 'extraction_timestamp', 'quality_analysis']]),
                            'confidence_score': extracted_data['quality_analysis']['confidence_score']
                        }
                    }
                )
                
            except Exception as e:
                # Update document with error
                if 'document' in locals():
                    document.processado = False
                    document.erro_processamento = str(e)
                    await db.commit()
                
                self.update_state(
                    state='FAILURE',
                    meta={'error': str(e)}
                )
                raise
    
    # Run async function
    import asyncio
    return asyncio.run(_process())

@celery_app.task(name="app.services.document_processor.process_bulk_documents_task")
def process_bulk_documents_task(document_ids: List[int]):
    """Process multiple documents in bulk"""
    results = []
    
    for doc_id in document_ids:
        try:
            result = process_document_task.delay(doc_id)
            results.append({
                'document_id': doc_id,
                'task_id': result.id,
                'status': 'queued'
            })
        except Exception as e:
            results.append({
                'document_id': doc_id,
                'error': str(e),
                'status': 'failed'
            })
    
    return results

def get_processing_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a processing task"""
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 100,
            'status': 'Task is pending...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 100),
            'status': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'current': 100,
            'total': 100,
            'status': 'Task completed successfully',
            'result': task.info.get('result', {})
        }
    else:
        response = {
            'state': task.state,
            'current': 0,
            'total': 100,
            'status': str(task.info),
            'error': task.info.get('error', 'Unknown error')
        }
    
    return response 