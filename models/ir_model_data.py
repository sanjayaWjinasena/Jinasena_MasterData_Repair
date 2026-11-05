# -*- coding: utf-8 -*-
"""Make the repair helpdesk teams the teams Odoo creates for each company, as on Clear-DB.

Odoo creates a 'Customer Care' team for every new company (helpdesk res.company.create). On Clear-DB those
teams were renamed and configured as the 'Customer Care - Repair' teams. Called from data/00_bind_teams.xml
before helpdesk.team.csv: our xmlid is bound to that company's Odoo-created team, so the CSV configures it
instead of adding a second team. On a database where the repair team already exists (installed before this
bind), the Odoo-created team is archived when it has no tickets.
"""
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

MODULE = 'Jinasena_MasterData_Repair'
SEED = 'seed_master_data_and_settings'
# our team xmlid -> company it belongs to on Clear-DB
REPAIR_TEAMS = {
    'helpdesk_team_customer_care_repair_1': f'{SEED}.company_jinasena_pvt_ltd',
    'helpdesk_team_customer_care_repair': f'{SEED}.company_jinasena_agricultural_machinery',
}


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def _jinasena_md_repair_bind_teams(self):
        IMD = self.sudo()
        Team = self.env['helpdesk.team'].sudo().with_context(active_test=False)
        for xmlid, company_xmlid in REPAIR_TEAMS.items():
            company = self.env.ref(company_xmlid, raise_if_not_found=False)
            if not company:
                continue
            with_xmlid = IMD.search([('model', '=', 'helpdesk.team')]).mapped('res_id')
            odoo_team = Team.search([('company_id', '=', company.id), ('name', '=', 'Customer Care'),
                                     ('id', 'not in', with_xmlid)], limit=1)
            if not odoo_team:
                continue
            if not IMD.search_count([('module', '=', MODULE), ('name', '=', xmlid)]):
                IMD.create({'module': MODULE, 'name': xmlid, 'model': 'helpdesk.team', 'res_id': odoo_team.id, 'noupdate': False})
                _logger.info('[%s] %s bound to the Customer Care team Odoo created for %s', MODULE, xmlid, company.name)
            elif not self.env['helpdesk.ticket'].sudo().with_context(active_test=False).search_count([('team_id', '=', odoo_team.id)]):
                odoo_team.active = False
                _logger.info('[%s] archived the unused Customer Care team of %s (the repair team exists)', MODULE, company.name)
        return True

    @api.model
    def _jinasena_md_repair_load_odoo_rows(self):
        """Apply our rows for Odoo's own stages / ticket types (helpdesk.stage_*, helpdesk.type_*) on upgrades too.

        Clear-DB renamed and re-used those records. Odoo keeps them noupdate, so the CSV load skips them when
        this module is upgraded; loading them here in install mode applies them, without changing Odoo's
        noupdate flags (a helpdesk upgrade keeps them as they are).
        """
        import csv
        import os
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        for model, rel in (('helpdesk.stage', 'helpdesk.stage.csv'), ('helpdesk.ticket.type', 'helpdesk.ticket.type.csv')):
            with open(os.path.join(data_dir, rel), encoding='utf-8-sig', newline='') as f:
                rows = list(csv.reader(f))
            header, ours = rows[0], [r for r in rows[1:] if r and r[0].startswith('helpdesk.')]
            if not ours:
                continue
            res = self.env[model].sudo().with_context(mode='init', noupdate=False).load(header, ours)
            errors = [m for m in res.get('messages', []) if m.get('type') == 'error']
            if errors:
                raise ValueError(f'{model}: {errors}')
            _logger.info('[%s] applied %s Clear-DB rows for Odoo %s records', MODULE, len(ours), model)
        return True
