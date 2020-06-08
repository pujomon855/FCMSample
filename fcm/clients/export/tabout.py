# -*- coding: utf-8 -*-

import openpyxl
import os

from fcm import settings


CLIENT_TABLE_FILE_PATH = os.path.join(settings.BASE_DIR, 'clients/static/clients/excel/FIXClientTable.xlsx')
CLIENT_TABLE_FILE_NAME = 'FIXClientTable.xlsx'


def create_client_table_xl():
    """
    顧客一覧エクセルを作成する。

    :return: (顧客一覧wb(未保存), ファイル名)
    """
    wb = openpyxl.load_workbook(CLIENT_TABLE_FILE_PATH)
    ws = wb.active
    ws.cell(row=3, column=1, value=2)
    # ws['A3'] = 1

    return wb, CLIENT_TABLE_FILE_NAME
