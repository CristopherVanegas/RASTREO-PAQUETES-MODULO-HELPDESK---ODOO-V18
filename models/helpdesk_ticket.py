# -- encoding: utf-8 --

from odoo import models, fields, api
from werkzeug.routing import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # ------------------------------------------------------
    # DEFAULT METHODS
    # ------------------------------------------------------
    @api.model
    def create(self, vals):
        # Crear el ticket de soporte
        ticket = super(HelpdeskTicket, self).create(vals)
        # Si package_names está presente, asignar invoice_number
        if ticket.package_names:
            ticket._assign_invoice_number()
        else:
            ticket.invoice_number = False  # Asegura que invoice_number esté vacío si package_names no está presente
        return ticket

    def write(self, vals):
        # Si el campo package_names cambia, actualizar invoice_number
        if 'package_names' in vals:
            self._assign_invoice_number()
        return super(HelpdeskTicket, self).write(vals)

    def _assign_invoice_number(self):
        # Buscar la factura vinculada al paquete
        if self.package_names:
            invoice = self.env['account.move'].search([
                ('package_ids.name', '=', self.package_names)
            ], limit=1)

            # Si la factura existe, asignar el número de factura
            if invoice and invoice.name:
                self.invoice_number = invoice.name
            else:
                self.invoice_number = False  # Si no se encuentra la factura, poner en blanco o None
                return {
                    'warning': {
                        'title': 'Factura no encontrada',
                        'message': 'No existe una factura que este relacionado al paquete que ingresó.'
                    }
                }
        else:
            self.invoice_number = False
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
