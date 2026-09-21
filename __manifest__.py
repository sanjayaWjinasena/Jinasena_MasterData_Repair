# -*- coding: utf-8 -*-
{
    'name': 'Jinasena : MasterData : Repair',
    'version': '17.0.0.0.2',
    'summary': 'Master-data extracted from CDB for Repair domain.',
    'description': 'Extracted from Clear-DB. Test-env master data. Edit the CSVs in data/ to add/remove rows before install.',
    'author': 'Jinasena Agricultural Machinery (Pvt) Ltd.',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'depends': [
        'Fix-repair',
        'Jinasena_MasterData_Common',
    ],
    'data': [
        'data/x_repair_stages.csv',
        'data/x_repair_reason_custom.csv',
        'data/x_repair_sub_reason.csv',
        'data/x_repair_accounts.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
