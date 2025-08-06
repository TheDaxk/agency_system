from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import tempfile
from sqlmodel import Session, select, func
from app.models.client import Client
from app.models.project import Project
from app.models.financial import FinancialEntry, EntryType
from app.models.service import Service

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos customizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#34495e')
        ))
        
        # Texto normal customizado
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Texto centralizado
        self.styles.add(ParagraphStyle(
            name='CustomCenter',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER
        ))

    def generate_client_report(self, client_data: Dict[str, Any], projects: List[Dict], 
                             financial_data: List[Dict], session: Session) -> str:
        """Gerar relatório de cliente"""
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Criar documento
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Cabeçalho
        story.append(Paragraph("AgênciaHub", self.styles['CustomTitle']))
        story.append(Paragraph("Relatório de Cliente", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        # Informações do cliente
        story.append(Paragraph("Informações do Cliente", self.styles['CustomSubtitle']))
        
        client_info = [
            ['Nome:', client_data.get('name', 'N/A')],
            ['Contato:', client_data.get('contact_name', 'N/A')],
            ['Email:', client_data.get('email', 'N/A')],
            ['Telefone:', client_data.get('phone', 'N/A')],
            ['Cidade:', client_data.get('city', 'N/A')],
            ['Status:', 'Ativo' if client_data.get('active', False) else 'Inativo']
        ]
        
        client_table = Table(client_info, colWidths=[2*inch, 4*inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(client_table)
        story.append(Spacer(1, 30))
        
        # Projetos
        if projects:
            story.append(Paragraph("Projetos", self.styles['CustomSubtitle']))
            
            project_data = [['Título', 'Status', 'Prioridade', 'Valor', 'Progresso']]
            
            for project in projects:
                status_map = {
                    'planning': 'Planejamento',
                    'in_progress': 'Em Progresso',
                    'review': 'Revisão',
                    'completed': 'Concluído',
                    'cancelled': 'Cancelado'
                }
                
                priority_map = {
                    'low': 'Baixa',
                    'medium': 'Média',
                    'high': 'Alta',
                    'urgent': 'Urgente'
                }
                
                value_str = f"R$ {project.get('value', 0):,.2f}" if project.get('value') else 'N/A'
                progress_str = f"{project.get('progress', 0)}%"
                
                project_data.append([
                    project.get('title', 'N/A'),
                    status_map.get(project.get('status'), project.get('status', 'N/A')),
                    priority_map.get(project.get('priority'), project.get('priority', 'N/A')),
                    value_str,
                    progress_str
                ])
            
            project_table = Table(project_data, colWidths=[2.5*inch, 1.2*inch, 1*inch, 1*inch, 0.8*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(project_table)
            story.append(Spacer(1, 30))
        
        # Resumo financeiro
        if financial_data:
            story.append(Paragraph("Resumo Financeiro", self.styles['CustomSubtitle']))
            
            total_income = sum(f.get('amount', 0) for f in financial_data if f.get('type') == 'income')
            total_expenses = sum(f.get('amount', 0) for f in financial_data if f.get('type') == 'expense')
            balance = total_income - total_expenses
            
            financial_summary = [
                ['Total de Receitas:', f"R$ {total_income:,.2f}"],
                ['Total de Despesas:', f"R$ {total_expenses:,.2f}"],
                ['Saldo:', f"R$ {balance:,.2f}"]
            ]
            
            financial_table = Table(financial_summary, colWidths=[2*inch, 2*inch])
            financial_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(financial_table)
        
        # Rodapé
        story.append(Spacer(1, 50))
        story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                              self.styles['CustomCenter']))
        
        # Construir PDF
        doc.build(story)
        
        return temp_file.name

    def generate_financial_report(self, start_date: datetime, end_date: datetime, 
                                session: Session) -> str:
        """Gerar relatório financeiro"""
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Criar documento
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Cabeçalho
        story.append(Paragraph("AgênciaHub", self.styles['CustomTitle']))
        story.append(Paragraph("Relatório Financeiro", self.styles['CustomSubtitle']))
        story.append(Paragraph(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}", 
                              self.styles['CustomCenter']))
        story.append(Spacer(1, 30))
        
        # Buscar dados financeiros
        financial_query = select(FinancialEntry).where(
            FinancialEntry.date >= start_date,
            FinancialEntry.date <= end_date
        ).order_by(FinancialEntry.date.desc())
        
        transactions = session.exec(financial_query).all()
        
        # Calcular totais
        total_income = sum(t.amount for t in transactions if t.type == EntryType.INCOME)
        total_expenses = sum(t.amount for t in transactions if t.type == EntryType.EXPENSE)
        net_profit = total_income - total_expenses
        profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
        
        # Resumo executivo
        story.append(Paragraph("Resumo Executivo", self.styles['CustomSubtitle']))
        
        summary_data = [
            ['Total de Receitas:', f"R$ {total_income:,.2f}"],
            ['Total de Despesas:', f"R$ {total_expenses:,.2f}"],
            ['Lucro Líquido:', f"R$ {net_profit:,.2f}"],
            ['Margem de Lucro:', f"{profit_margin:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Receitas por categoria
        income_by_category = {}
        expense_by_category = {}
        
        for transaction in transactions:
            if transaction.type == EntryType.INCOME:
                income_by_category[transaction.category] = income_by_category.get(transaction.category, 0) + transaction.amount
            else:
                expense_by_category[transaction.category] = expense_by_category.get(transaction.category, 0) + transaction.amount
        
        if income_by_category:
            story.append(Paragraph("Receitas por Categoria", self.styles['CustomSubtitle']))
            
            income_data = [['Categoria', 'Valor', 'Percentual']]
            for category, amount in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                income_data.append([category, f"R$ {amount:,.2f}", f"{percentage:.1f}%"])
            
            income_table = Table(income_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            income_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(income_table)
            story.append(Spacer(1, 20))
        
        if expense_by_category:
            story.append(Paragraph("Despesas por Categoria", self.styles['CustomSubtitle']))
            
            expense_data = [['Categoria', 'Valor', 'Percentual']]
            for category, amount in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                expense_data.append([category, f"R$ {amount:,.2f}", f"{percentage:.1f}%"])
            
            expense_table = Table(expense_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            expense_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(expense_table)
            story.append(Spacer(1, 20))
        
        # Transações detalhadas (últimas 20)
        story.append(Paragraph("Transações Recentes", self.styles['CustomSubtitle']))
        
        transaction_data = [['Data', 'Descrição', 'Categoria', 'Tipo', 'Valor']]
        
        for transaction in transactions[:20]:  # Últimas 20 transações
            type_text = 'Receita' if transaction.type == EntryType.INCOME else 'Despesa'
            value_text = f"R$ {transaction.amount:,.2f}"
            if transaction.type == EntryType.EXPENSE:
                value_text = f"-{value_text}"
            
            transaction_data.append([
                transaction.date.strftime('%d/%m/%Y'),
                transaction.description[:30] + '...' if len(transaction.description) > 30 else transaction.description,
                transaction.category,
                type_text,
                value_text
            ])
        
        transaction_table = Table(transaction_data, colWidths=[1*inch, 2.2*inch, 1.3*inch, 0.8*inch, 1.2*inch])
        transaction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(transaction_table)
        
        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                              self.styles['CustomCenter']))
        
        # Construir PDF
        doc.build(story)
        
        return temp_file.name

    def generate_project_report(self, project_data: Dict[str, Any], client_data: Dict[str, Any],
                              services: List[Dict], session: Session) -> str:
        """Gerar relatório de projeto"""
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Criar documento
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Cabeçalho
        story.append(Paragraph("AgênciaHub", self.styles['CustomTitle']))
        story.append(Paragraph("Relatório de Projeto", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        # Informações do projeto
        story.append(Paragraph("Informações do Projeto", self.styles['CustomSubtitle']))
        
        status_map = {
            'planning': 'Planejamento',
            'in_progress': 'Em Progresso',
            'review': 'Revisão',
            'completed': 'Concluído',
            'cancelled': 'Cancelado'
        }
        
        priority_map = {
            'low': 'Baixa',
            'medium': 'Média',
            'high': 'Alta',
            'urgent': 'Urgente'
        }
        
        project_info = [
            ['Título:', project_data.get('title', 'N/A')],
            ['Cliente:', client_data.get('name', 'N/A')],
            ['Status:', status_map.get(project_data.get('status'), project_data.get('status', 'N/A'))],
            ['Prioridade:', priority_map.get(project_data.get('priority'), project_data.get('priority', 'N/A'))],
            ['Valor:', f"R$ {project_data.get('value', 0):,.2f}" if project_data.get('value') else 'N/A'],
            ['Progresso:', f"{project_data.get('progress', 0)}%"],
            ['Data de Criação:', project_data.get('created_at', 'N/A')],
            ['Prazo:', project_data.get('deadline', 'N/A')]
        ]
        
        project_table = Table(project_info, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(project_table)
        story.append(Spacer(1, 30))
        
        # Descrição do projeto
        if project_data.get('description'):
            story.append(Paragraph("Descrição", self.styles['CustomSubtitle']))
            story.append(Paragraph(project_data['description'], self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
        
        # Serviços/Tarefas
        if services:
            story.append(Paragraph("Serviços/Tarefas", self.styles['CustomSubtitle']))
            
            service_data = [['Descrição', 'Status', 'Valor', 'Data']]
            
            for service in services:
                service_data.append([
                    service.get('description', 'N/A'),
                    service.get('status', 'N/A'),
                    f"R$ {service.get('value', 0):,.2f}" if service.get('value') else 'N/A',
                    service.get('date', 'N/A')
                ])
            
            service_table = Table(service_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
            service_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(service_table)
            story.append(Spacer(1, 20))
        
        # Observações
        if project_data.get('notes'):
            story.append(Paragraph("Observações", self.styles['CustomSubtitle']))
            story.append(Paragraph(project_data['notes'], self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
        
        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                              self.styles['CustomCenter']))
        
        # Construir PDF
        doc.build(story)
        
        return temp_file.name

    def generate_invoice(self, client_data: Dict[str, Any], project_data: Dict[str, Any],
                        services: List[Dict], invoice_data: Dict[str, Any]) -> str:
        """Gerar fatura/orçamento"""
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Criar documento
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Cabeçalho da empresa
        story.append(Paragraph("AgênciaHub", self.styles['CustomTitle']))
        story.append(Paragraph("Agência Digital", self.styles['CustomCenter']))
        story.append(Paragraph("contato@agenciahub.com | (11) 99999-9999", self.styles['CustomCenter']))
        story.append(Spacer(1, 30))
        
        # Tipo de documento
        doc_type = invoice_data.get('type', 'invoice')
        doc_title = 'FATURA' if doc_type == 'invoice' else 'ORÇAMENTO'
        story.append(Paragraph(doc_title, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        # Informações do cliente e projeto
        info_data = [
            ['Cliente:', client_data.get('name', 'N/A'), 'Número:', invoice_data.get('number', 'N/A')],
            ['Contato:', client_data.get('contact_name', 'N/A'), 'Data:', invoice_data.get('date', datetime.now().strftime('%d/%m/%Y'))],
            ['Email:', client_data.get('email', 'N/A'), 'Vencimento:', invoice_data.get('due_date', 'N/A')],
            ['Projeto:', project_data.get('title', 'N/A'), 'Status:', invoice_data.get('status', 'Pendente')]
        ]
        
        info_table = Table(info_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Itens/Serviços
        story.append(Paragraph("Itens", self.styles['CustomSubtitle']))
        
        items_data = [['Descrição', 'Qtd', 'Valor Unit.', 'Total']]
        subtotal = 0
        
        for service in services:
            quantity = service.get('quantity', 1)
            unit_value = service.get('value', 0)
            total_value = quantity * unit_value
            subtotal += total_value
            
            items_data.append([
                service.get('description', 'N/A'),
                str(quantity),
                f"R$ {unit_value:,.2f}",
                f"R$ {total_value:,.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Descrição alinhada à esquerda
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Totais
        discount = invoice_data.get('discount', 0)
        tax = invoice_data.get('tax', 0)
        total = subtotal - discount + tax
        
        totals_data = [
            ['Subtotal:', f"R$ {subtotal:,.2f}"],
            ['Desconto:', f"R$ {discount:,.2f}"],
            ['Impostos:', f"R$ {tax:,.2f}"],
            ['TOTAL:', f"R$ {total:,.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Alinhar tabela de totais à direita
        story.append(Spacer(1, 10))
        story.append(Table([[totals_table]], colWidths=[6.5*inch]))
        
        # Observações
        if invoice_data.get('notes'):
            story.append(Spacer(1, 30))
            story.append(Paragraph("Observações", self.styles['CustomSubtitle']))
            story.append(Paragraph(invoice_data['notes'], self.styles['CustomNormal']))
        
        # Termos e condições
        story.append(Spacer(1, 30))
        story.append(Paragraph("Termos e Condições", self.styles['CustomSubtitle']))
        terms = """
        1. Pagamento deve ser efetuado até a data de vencimento.
        2. Após o vencimento, será cobrada multa de 2% ao mês.
        3. Os serviços serão executados conforme especificação acordada.
        4. Alterações no escopo podem gerar custos adicionais.
        """
        story.append(Paragraph(terms, self.styles['CustomNormal']))
        
        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                              self.styles['CustomCenter']))
        
        # Construir PDF
        doc.build(story)
        
        return temp_file.name

    def cleanup_temp_file(self, file_path: str):
        """Limpar arquivo temporário"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Erro ao limpar arquivo temporário: {e}")

