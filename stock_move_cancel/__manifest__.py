# -*- coding: utf-8 -*-

{
    "name": "Reset Stock Move",
    "version": "10.0.1.0",
    "author": "Oscar Morocho <om@prisehub.com>",
    "category": "Warehouse",
    "website": "http://www.prisehub.com",
    'summary': 'Este módulo ayuda a revertir los movimientos realizados, permite cancelar y establecer en borrador los moviminetos',
    "depends": [
        "stock","sale_stock","stock_picking_cancel",
    ],
    'description': """
    """,
    "data": [
        "security/move_security.xml",
        "views/stock_move_view.xml"
    ],
    "installable": True,
    "auto_install": False,
}
