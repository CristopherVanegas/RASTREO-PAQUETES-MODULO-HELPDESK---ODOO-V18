# -- encoding: utf-8 --

from odoo import models, fields, api
from werkzeug.routing import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # ------------------------------------------------------
    # DEFAULT METHODS
    # ------------------------------------------------------
    @api.model
    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        # Si el campo package_names cambia, actualizar invoice_number
        invoice = self.env['account.move'].search([
            ('package_ids.name', '=', self.package_names)
        ], limit=1)
        if self.package_names and not invoice:
            raise ValidationError('No existe una factura que este relacionado al paquete que ingresó.')
        return res
    # ------------------------------------------------------
    # COMPUTE AND INVERSE METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # SELECTION METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # CONSTRAINTS AND VALIDATIONS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # ONCHANGE METHODS
    # ------------------------------------------------------
    @api.onchange('client_type')
    def _onchange_client_type(self):
        # Si client_type está lleno
        if self.client_type:
            # Asignamos el equipo "Atención VIP" si es un cliente VIP
            self.team_id = self.env['helpdesk.team'].search([('name', '=', 'Atención VIP')], limit=1).id
        else:
            # Si no es VIP, asignamos el equipo "Atención al cliente"
            self.team_id = self.env['helpdesk.team'].search([('name', '=', 'Atención al cliente')], limit=1).id

    @api.onchange('package_names')
    def _onchange_package_names(self):
        if self.package_names:  # Verifica si package_names no es vacío
            # Buscar la factura basada en los paquetes
            invoice = self.env['account.move'].search([
                ('package_ids.name', '=', self.package_names)
            ], limit=1)

            if invoice and invoice.name:
                self.invoice_number = invoice.name
            else:
                self.invoice_number = False  # Si no se encuentra la factura
                return {
                    'warning': {
                        'title': 'Factura no encontrada',
                        'message': 'No existe una factura que este relacionado al paquete que ingresó.'
                    }
                }
        else:
            self.invoice_number = False
    # ------------------------------------------------------
    # CRUD METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # OTHER METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # VARIABLES
    # ------------------------------------------------------

    package_names = fields.Char(string='Número de Paquete', required=True, store=True)
    invoice_number = fields.Char(string='Número de Factura', required=True, readonly=True, store=True)
    client_type = fields.Many2one('client.classification', related='partner_id.client_type', string="Clasificación Cliente", readonly=True, store=True)
    team_id = fields.Many2one('helpdesk.team', string="Equipo", readonly=True) 
