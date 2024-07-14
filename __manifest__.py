{
    "name": "Video Game Truck",
    "description": "Video Game Truck Truck Demo",
    "version": "1.0",
    "author": "Dynamic Solution Innovators Ltd.",
    "category": "Websites",
    "depends": ["base", "website", "website_sale"],
    "data": [
        # security
        "security/ir.model.access.csv",
        # views
        "views/pricing_template.xml",
        "views/service_schedule.xml",
        'views/product_template_views.xml',
        "views/video_game_truck_views.xml",
        "views/slot_views.xml",
        # menu
        "views/menu_items.xml",
        "views/module_template.xml",
    ],
    "installable": True,
    "application": True,
    # For free version use LGPL-3, for paid one change it to OPL-1
    "license": "LGPL-3"
}
