"""
PDF Processor - research_analyzer.py'den adapt edilmiş
Async ve web-friendly PDF table extraction
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import time
from datetime import datetime
import pandas as pd

# Research analyzer modülünü import et
sys.path.append('../../')  # Ana dizine git
try:
    from pdf_table_extractor import PDFTableExtractor
    from smart_aggregator import SmartAggregator
except ImportError as e:
    print(f"Modül import hatası: {e}")

class PDFProcessor:
    """PDF işleme motoru - research_analyzer.py'den adapt edilmiş"""
    
    def __init__(self):
        self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Varsayılan konfigürasyon - research_analyzer.py'den"""
        return {
            # Extraction ayarları
            'extraction_methods': ['camelot', 'pdfplumber', 'tabula'],
            'log_level': 'INFO',
            'include_metadata': True,
            'create_summary_sheet': True,
            
            # Numeric focus (research reports için optimize)
            'focus_numeric': True,
            'numeric_threshold': 0.3,
            'min_numeric_columns': 1,
            'smart_header_detection': True,
            'professional_formatting': True,
            'preserve_layout': True,
            
            # Analysis ayarları
            'auto_categorize': True,
            'extract_key_metrics': True,
            'generate_trends': True,
            'similarity_threshold': 0.8,
            'min_data_quality': 0.5,
            
            # Performance
            'max_processing_time': 300,
            'enable_caching': True,
            'parallel_processing': False
        }
    
    async def process_pdf(
        self, 
        pdf_path: str, 
        job_id: str, 
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        PDF'i işle ve tabloları çıkar
        
        Args:
            pdf_path: PDF dosya yolu
            job_id: İş ID'si
            progress_callback: Progress update callback
            
        Returns:
            İşlem sonucu
        """
        try:
            start_time = time.time()
            
            if progress_callback:
                await progress_callback(10)
            
            # Çıktı dizini hazırla
            output_dir = Path(f"../results/{job_id}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: PDF Table Extraction
            if progress_callback:
                await progress_callback(20)
            
            extraction_result = await self._extract_tables_async(pdf_path, output_dir, progress_callback)
            
            if not extraction_result['success']:
                return {
                    'success': False,
                    'error': extraction_result.get('error', 'Extraction failed'),
                    'tables': []
                }
            
            # Step 2: Smart Analysis (optional)
            if progress_callback:
                await progress_callback(60)
            
            analysis_result = await self._analyze_tables_async(
                extraction_result['excel_path'], 
                output_dir, 
                progress_callback
            )
            
            # Step 3: Format results for web
            if progress_callback:
                await progress_callback(90)
            
            web_tables = await self._format_for_web(analysis_result, output_dir)
            
            if progress_callback:
                await progress_callback(100)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'tables': web_tables,
                'excel_path': extraction_result['excel_path'],
                'processing_time': processing_time,
                'job_id': job_id,
                'analysis_summary': analysis_result.get('summary_metrics', {}),
                'table_count': len(web_tables)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tables': []
            }
    
    async def _extract_tables_async(
        self, 
        pdf_path: str, 
        output_dir: Path, 
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Async tablo çıkarma"""
        try:
            # PDFTableExtractor konfigürasyonu
            extractor_config = {
                'output_dir': str(output_dir / 'tables'),
                'extraction_methods': self.config['extraction_methods'],
                'log_level': self.config['log_level'],
                'include_metadata': self.config['include_metadata'],
                'create_summary_sheet': self.config['create_summary_sheet'],
                'focus_numeric': self.config['focus_numeric'],
                'numeric_threshold': self.config['numeric_threshold'],
                'min_numeric_columns': self.config['min_numeric_columns'],
                'min_table_rows': 2,
                'min_table_cols': 2,
                'smart_header_detection': self.config['smart_header_detection'],
                'professional_formatting': self.config['professional_formatting'],
                'preserve_layout': self.config['preserve_layout']
            }
            
            # Executor thread'de çalıştır (blocking operation)
            loop = asyncio.get_event_loop()
            
            def run_extraction():
                extractor = PDFTableExtractor(extractor_config)
                return extractor.process_single_pdf(pdf_path)
            
            excel_path = await loop.run_in_executor(None, run_extraction)
            
            if progress_callback:
                await progress_callback(40)
            
            return {
                'success': True,
                'excel_path': excel_path,
                'message': f"Tablolar başarıyla çıkarıldı: {excel_path}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Extraction hatası: {e}"
            }
    
    async def _analyze_tables_async(
        self, 
        excel_path: str, 
        output_dir: Path, 
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Async akıllı analiz"""
        try:
            loop = asyncio.get_event_loop()
            
            def run_analysis():
                aggregator = SmartAggregator(self.config)
                return aggregator.smart_aggregate(excel_path)
            
            analysis_result = await loop.run_in_executor(None, run_analysis)
            
            if progress_callback:
                await progress_callback(80)
            
            return analysis_result
            
        except Exception as e:
            # Analiz başarısız olsa da extraction'ı döndür
            return {
                'error': str(e),
                'message': f"Analysis hatası: {e}",
                'summary_metrics': {}
            }
    
    async def _format_for_web(self, analysis_result: Dict, output_dir: Path) -> List[Dict]:
        """Web interface için formatla"""
        try:
            web_tables = []
            
            # Excel dosyasından tabloları oku
            excel_path = analysis_result.get('source_file')
            if excel_path and Path(excel_path).exists():
                excel_file = pd.ExcelFile(excel_path)
                
                for sheet_name in excel_file.sheet_names:
                    if sheet_name.lower() in ['summary', 'metadata']:
                        continue
                    
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    
                    # Boş DataFrame'leri atla
                    if df.empty:
                        continue
                    
                    # Web formatına çevir
                    table_data = {
                        'name': sheet_name,
                        'shape': [len(df), len(df.columns)],
                        'columns': df.columns.tolist(),
                        'data': df.head(100).fillna('').to_dict('records'),  # İlk 100 satır
                        'row_count': len(df),
                        'col_count': len(df.columns),
                        'has_numeric': any(df.dtypes.apply(lambda x: pd.api.types.is_numeric_dtype(x))),
                        'preview_only': len(df) > 100,
                        'data_types': df.dtypes.astype(str).to_dict()
                    }
                    
                    # Kategorize et (analysis result'tan)
                    category = self._categorize_table(sheet_name, df, analysis_result)
                    table_data['category'] = category
                    
                    # Quality score
                    quality_score = self._calculate_quality_score(df)
                    table_data['quality_score'] = quality_score
                    
                    web_tables.append(table_data)
            
            return web_tables
            
        except Exception as e:
            print(f"Web formatting error: {e}")
            return []
    
    def _categorize_table(self, sheet_name: str, df: pd.DataFrame, analysis_result: Dict) -> str:
        """Tabloyu kategorize et"""
        # Analysis result'tan kategori bilgisi al
        categorized_tables = analysis_result.get('categorized_tables', {})
        
        for category, tables in categorized_tables.items():
            if any(sheet_name in str(table) for table in tables):
                return category.replace('_', ' ').title()
        
        # Fallback kategorization
        sheet_lower = sheet_name.lower()
        
        if any(keyword in sheet_lower for keyword in ['financial', 'finance', 'revenue', 'cost', 'budget']):
            return 'Financial Data'
        elif any(keyword in sheet_lower for keyword in ['performance', 'metric', 'kpi', 'indicator']):
            return 'Performance Metrics'
        elif any(keyword in sheet_lower for keyword in ['summary', 'overview', 'total']):
            return 'Summary Tables'
        elif any(keyword in sheet_lower for keyword in ['detail', 'breakdown', 'analysis']):
            return 'Detailed Analysis'
        else:
            return 'General Data'
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Tablo kalite skoru hesapla"""
        try:
            # Temel metrikler
            total_cells = len(df) * len(df.columns)
            if total_cells == 0:
                return 0.0
            
            # Boş hücre oranı
            null_ratio = df.isnull().sum().sum() / total_cells
            
            # Numeric veri oranı
            numeric_cols = df.select_dtypes(include=['number']).columns
            numeric_ratio = len(numeric_cols) / len(df.columns) if len(df.columns) > 0 else 0
            
            # Veri çeşitliliği
            unique_ratio = df.nunique().mean() / len(df) if len(df) > 0 else 0
            unique_ratio = min(unique_ratio, 1.0)  # Cap at 1.0
            
            # Genel kalite skoru
            quality_score = (
                (1 - null_ratio) * 0.4 +  # Null değer az olsun
                numeric_ratio * 0.3 +      # Numeric veri fazla olsun
                unique_ratio * 0.3         # Çeşitlilik olsun
            )
            
            return round(quality_score, 2)
            
        except Exception:
            return 0.5  # Default score 