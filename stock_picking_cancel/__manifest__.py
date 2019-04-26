# -*- coding: utf-8 -*-

{
    "name": "Stock Picking Cancel Reverse",
    "version": "10.0.1.3",
    "author": "Oscar Morocho<om@prisehub.com>",
    "category": "Warehouse",
    "website": "http://www.prisehub.com",
    'summary': 'Este módulo ayuda a cancelar/revertir los pickings en estado realizado',
    "depends": [
        "stock","sale_stock",
    ],
    'description': """
        """,
    "data": [
        "security/picking_security.xml",
        "views/stock_view.xml"
    ],
    "installable": True,
    "auto_install": False,
}
