{
    'name': 'TRAMACO PRUEBA',
    'version': '1.0',
    'category': '',
    'summary': 'Mejora la atención de clienntes VIP y no VIP al rastrear los paquetes.',
    'description': """
        Autores:
            - Cristopher Vanegas
    """,
    'license': 'OEEL-1',
    'maintainer': 'TRESCLOUD CIA. LTDA.',
    'depends': ['base', 'contacts', 'accountant', 'helpdesk'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        # reports
        # wizard
        # views
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/client_classification_views.xml',
    ],
    'installable': True,
    'application': False,
}
