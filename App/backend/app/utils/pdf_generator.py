"""
PDF generation utilities using ReportLab
"""
from datetime import datetime, date
from typing import List, Dict, Any
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class WeCarePDFGenerator:
    """PDF generator for We Care reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the PDF"""
        styles = {}
        
        # Title style
        styles['title'] = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c5282')
        )
        
        # Subtitle style
        styles['subtitle'] = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4a5568')
        )
        
        # Header style
        styles['header'] = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2d3748')
        )
        
        # Body style
        styles['body'] = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        return styles
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#2c5282'))
        canvas.drawString(50, A4[1] - 50, "We Care - Sistema de Gestão Operacional")
        
        # Add line under header
        canvas.setStrokeColor(colors.HexColor('#2c5282'))
        canvas.setLineWidth(2)
        canvas.line(50, A4[1] - 65, A4[0] - 50, A4[1] - 65)
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(50, 30, f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        canvas.drawRightString(A4[0] - 50, 30, f"Página {doc.page}")
        
        canvas.restoreState()
    
    def generate_checkin_report(self, checkins: List[Dict[str, Any]], filters: Dict[str, Any]) -> bytes:
        """Generate check-in report PDF"""
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=100,
            bottomMargin=50
        )
        
        # Build content
        story = []
        
        # Title
        title = Paragraph("Relatório de Check-ins", self.custom_styles['title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Filters info
        filter_info = []
        if filters.get('data_inicio') and filters.get('data_fim'):
            filter_info.append(f"Período: {filters['data_inicio']} a {filters['data_fim']}")
        
        if filters.get('usuario_nome'):
            filter_info.append(f"Usuário: {filters['usuario_nome']}")
        
        if filter_info:
            filters_text = " | ".join(filter_info)
            subtitle = Paragraph(filters_text, self.custom_styles['subtitle'])
            story.append(subtitle)
            story.append(Spacer(1, 20))
        
        # Summary
        total_checkins = len(checkins)
        realizados = len([c for c in checkins if c.get('status') == 'REALIZADO'])
        fora_local = len([c for c in checkins if c.get('status') == 'FORA_DE_LOCAL'])
        
        summary_data = [
            ['Total de Check-ins', str(total_checkins)],
            ['Realizados Corretamente', str(realizados)],
            ['Fora do Local', str(fora_local)],
            ['Taxa de Sucesso', f"{(realizados/total_checkins*100):.1f}%" if total_checkins > 0 else "0%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[4*cm, 3*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        
        story.append(Paragraph("Resumo", self.custom_styles['header']))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Detailed data
        if checkins:
            story.append(Paragraph("Detalhamento", self.custom_styles['header']))
            
            # Table headers
            table_data = [
                ['Data/Hora', 'Usuário', 'Status', 'Localização']
            ]
            
            # Add data rows
            for checkin in checkins:
                table_data.append([
                    checkin.get('data_hora_checkin', '').strftime('%d/%m/%Y %H:%M') if checkin.get('data_hora_checkin') else '',
                    checkin.get('usuario_nome', ''),
                    checkin.get('status', ''),
                    checkin.get('endereco', '')[:30] + '...' if checkin.get('endereco', '') else ''
                ])
            
            # Create table
            detail_table = Table(table_data, colWidths=[3.5*cm, 4*cm, 2.5*cm, 5*cm])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
            ]))
            
            story.append(detail_table)
        else:
            story.append(Paragraph("Nenhum check-in encontrado para os filtros selecionados.", self.custom_styles['body']))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def generate_hours_report(self, hours_data: List[Dict[str, Any]], filters: Dict[str, Any]) -> bytes:
        """Generate worked hours report PDF"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=100,
            bottomMargin=50
        )
        
        story = []
        
        # Title
        title = Paragraph("Relatório de Horas Trabalhadas", self.custom_styles['title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Period info
        if filters.get('periodo_inicio') and filters.get('periodo_fim'):
            period_text = f"Período: {filters['periodo_inicio']} a {filters['periodo_fim']}"
            subtitle = Paragraph(period_text, self.custom_styles['subtitle'])
            story.append(subtitle)
            story.append(Spacer(1, 20))
        
        # Summary by user
        if hours_data:
            # Create summary table
            table_data = [
                ['Usuário', 'Total Horas', 'Total Plantões', 'Média por Plantão']
            ]
            
            total_hours_all = 0
            total_shifts_all = 0
            
            for user_data in hours_data:
                total_hours = user_data.get('total_horas', 0)
                total_shifts = user_data.get('total_plantoes', 0)
                avg_hours = user_data.get('media_horas_por_plantao', 0)
                
                total_hours_all += total_hours
                total_shifts_all += total_shifts
                
                table_data.append([
                    user_data.get('usuario_nome', ''),
                    f"{total_hours:.1f}h",
                    str(total_shifts),
                    f"{avg_hours:.1f}h"
                ])
            
            # Add totals row
            table_data.append([
                'TOTAL',
                f"{total_hours_all:.1f}h",
                str(total_shifts_all),
                f"{total_hours_all/total_shifts_all:.1f}h" if total_shifts_all > 0 else "0h"
            ])
            
            # Create table
            hours_table = Table(table_data, colWidths=[5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
            hours_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#edf2f7')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2d3748')),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f7fafc')])
            ]))
            
            story.append(hours_table)
        else:
            story.append(Paragraph("Nenhum dado de horas encontrado para o período selecionado.", self.custom_styles['body']))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def generate_performance_report(self, performance_data: Dict[str, Any]) -> bytes:
        """Generate performance report PDF"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=100,
            bottomMargin=50
        )
        
        story = []
        
        # Title
        title = Paragraph("Relatório de Performance", self.custom_styles['title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Period info
        stats = performance_data.get('estatisticas_gerais', {})
        period = stats.get('periodo', {})
        
        if period:
            period_text = f"Período: {period.get('inicio')} a {period.get('fim')}"
            subtitle = Paragraph(period_text, self.custom_styles['subtitle'])
            story.append(subtitle)
            story.append(Spacer(1, 20))
        
        # Overall statistics
        story.append(Paragraph("Estatísticas Gerais", self.custom_styles['header']))
        
        general_stats = [
            ['Sócios Ativos', str(stats.get('total_socios_ativos', 0))],
            ['Média de Presença', f"{stats.get('media_taxa_presenca', 0):.1f}%"]
        ]
        
        general_table = Table(general_stats, colWidths=[4*cm, 3*cm])
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#edf2f7')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        
        story.append(general_table)
        story.append(Spacer(1, 20))
        
        # Individual performance
        individual_data = performance_data.get('performance_individual', [])
        
        if individual_data:
            story.append(Paragraph("Performance Individual", self.custom_styles['header']))
            
            # Sort by attendance rate
            individual_data.sort(key=lambda x: x.get('taxa_presenca', 0), reverse=True)
            
            # Create table
            table_data = [
                ['Usuário', 'Escalas', 'Check-ins', 'Taxa Presença']
            ]
            
            for user in individual_data:
                table_data.append([
                    user.get('nome', ''),
                    str(user.get('total_escalas', 0)),
                    str(user.get('checkins_realizados', 0)),
                    f"{user.get('taxa_presenca', 0):.1f}%"
                ])
            
            performance_table = Table(table_data, colWidths=[5*cm, 2*cm, 2*cm, 2.5*cm])
            performance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
            ]))
            
            story.append(performance_table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content


# Convenience functions
def generate_checkin_pdf(checkins_data: List[Dict], filters: Dict) -> bytes:
    """Generate check-in report PDF"""
    generator = WeCarePDFGenerator()
    return generator.generate_checkin_report(checkins_data, filters)


def generate_hours_pdf(hours_data: List[Dict], filters: Dict) -> bytes:
    """Generate hours report PDF"""
    generator = WeCarePDFGenerator()
    return generator.generate_hours_report(hours_data, filters)


def generate_performance_pdf(performance_data: Dict) -> bytes:
    """Generate performance report PDF"""
    generator = WeCarePDFGenerator()
    return generator.generate_performance_report(performance_data) 