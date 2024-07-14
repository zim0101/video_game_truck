from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    video_game_truck_ids = fields.One2many(
        'video_game_truck.truck',
        'product_id',
        string='Video Game Trucks',
        domain="[('product_id', '=', False)]"
    )
