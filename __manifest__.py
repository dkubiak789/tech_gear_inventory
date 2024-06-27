{
    "name": "Tech Gear Inventory",
    "version": "17.0.1.0.0",
    "summary": "Module to manage tech gear inventory",
    "category": "Inventory",
    "author": "Dariusz Kubiak",
    "depends": ["base", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/product_import_wizard_views.xml",
    ],
    "demo": [],
    "installable": True,
    "external_dependencies": {
        "python": ["pandas"],
    },
    "license": "LGPL-3",
}
