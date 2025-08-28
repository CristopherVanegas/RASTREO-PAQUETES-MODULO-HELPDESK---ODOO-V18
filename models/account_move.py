# -- encoding: utf-8 --

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ------------------------------------------------------
    # DEFAULT METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # COMPUTE AND INVERSE METHODS
    # ------------------------------------------------------
    @api.depends('package_ids')
    def _compute_package_names(self):
        for move in self:
            names = sorted(set(move.package_ids.mapped('name') or []))
            move.package_names = ', '.join(names) if names else False

    @api.depends('invoice_origin', 'line_ids.sale_line_ids')
    def _compute_package_ids(self):
        StockPicking = self.env['stock.picking']
        StockQuantPackage = self.env['stock.quant.package']
        StockMoveLine = self.env['stock.move.line']

        for move in self:
            packages = StockQuantPackage.browse()
            pickings = StockPicking.browse()
            so_names = []

            # 1) SOs desde invoice_origin (puede haber varias separadas por coma)
            if move.invoice_origin:
                so_names = [n.strip() for n in move.invoice_origin.split(',') if n.strip()]
            sale_orders = self.env['sale.order'].search([('name', 'in', so_names)]) if so_names else self.env[
                'sale.order'].browse()

            # 2) Respaldo: deducir SO por las sale_line_ids de las líneas de factura
            if not sale_orders and move.line_ids:
                sol = move.line_ids.mapped('sale_line_ids')
                sale_orders = sol.mapped('order_id')

            # --- PICKINGS VINCULADOS ---
            # A) Buscar Pickings directamente de las órdenes de venta
            if sale_orders:
                pickings |= StockPicking.search([
                    ('origin', 'in', so_names),  # Usamos origin para vincular con SO
                    ('picking_type_code', '=', 'outgoing'),
                    ('state', 'in', ['assigned', 'done']),
                ])

            pickings = pickings.exists()

            # --- PAQUETES ---

            # 1) Paquetes desde package_level_ids
            package_levels = pickings.mapped('package_level_ids')
            packages |= package_levels.mapped('package_id')

            # 2) Respaldo: desde líneas de movimiento de los pickings
            if pickings:
                mls = StockMoveLine.search([('picking_id', 'in', pickings.ids)])
                packages |= (mls.mapped('result_package_id') | mls.mapped('package_id'))

            move.package_ids = [(6, 0, packages.exists().ids)]

    # ------------------------------------------------------
    # SELECTION METHODS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # CONSTRAINTS AND VALIDATIONS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # ONCHANGE METHODS
    # ------------------------------------------------------

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
    package_names = fields.Char(
        string="Paquetes (Picking)",
        compute="_compute_package_names",
        store=True,
        help="Lista de códigos de paquete (stock.quant.package.name) "
             "vinculados a los albaranes de entrega de la(s) orden(es) de venta que originaron esta factura."
    )
    package_ids = fields.Many2many(
        comodel_name="stock.quant.package",
        string="Paquetes vinculados",
        compute="_compute_package_ids",
        store=True,
        help="Relación directa a los paquetes detectados."
    )