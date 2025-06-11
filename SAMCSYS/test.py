# tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timezone
from .models import (
    DETB_JRNL_LOG, MTTB_GLSub, MTTB_Ccy_DEFN, MTTB_TRN_Code, 
    MTTB_Fin_Cycle, MTTB_Per_Code, MTTB_Users, STTB_ModulesInfo,
    MTTB_GLMaster
)

class JournalEntryAPITestCase(APITestCase):
    def test_batch_create_balanced_entries(self):
        """Test creating balanced journal entries in batch"""
        data = {
            'Reference_No': 'BATCH-250609-00001',
            'Ccy_cd': self.currency.ccy_code,
            'Txn_code': self.txn_code.trn_code,
            'Value_date': '2025-06-09T10:30:00Z',
            'Addl_text': 'Batch transfer test',
            'fin_cycle': self.fin_cycle.fin_cycle,
            'Period_code': self.period.period_code,
            'module_id': self.module.module_Id,
            'entries': [
                {
                    'Account': self.account1.glsub_id,
                    'Amount': '500.00',
                    'Dr_cr': 'D'
                },
                {
                    'Account': self.account2.glsub_id,
                    'Amount': '500.00',
                    'Dr_cr': 'C'
                }
            ]
        }
        
        url = reverse('journal-entry-batch-create')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DETB_JRNL_LOG.objects.count(), 2)
        
        # Check balance
        entries = DETB_JRNL_LOG.objects.filter(Reference_No='BATCH-250609-00001')
        total_dr = sum(entry.lcy_dr or 0 for entry in entries)
        total_cr = sum(entry.lcy_cr or 0 for entry in entries)
        self.assertEqual(total_dr, total_cr)
    
    def test_batch_create_unbalanced_entries_fails(self):
        """Test that unbalanced entries are rejected"""
        data = {
            'Reference_No': 'UNBALANCED-250609-00001',
            'Ccy_cd': self.currency.ccy_code,
            'Txn_code': self.txn_code.trn_code,
            'Value_date': '2025-06-09T10:30:00Z',
            'entries': [
                {
                    'Account': self.account1.glsub_id,
                    'Amount': '500.00',
                    'Dr_cr': 'D'
                },
                {
                    'Account': self.account2.glsub_id,
                    'Amount': '300.00',  # Unbalanced amount
                    'Dr_cr': 'C'
                }
            ]
        }
        
        url = reverse('journal-entry-batch-create')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DETB_JRNL_LOG.objects.count(), 0)