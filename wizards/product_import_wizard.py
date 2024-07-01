import base64
from io import BytesIO

import pandas as pd

from odoo import fields, models
from odoo.exceptions import ValidationError


class ProductImportWizard(models.TransientModel):
    _name = "product.import.wizard"
    _description = "Product Import Wizard"

    data_file = fields.Binary("Excel File", required=True)

    def _decode_file_content(self):
        file_content = base64.b64decode(self.data_file)
        file_stream = BytesIO(file_content)
        return pd.read_excel(file_stream, engine="openpyxl")

    def _find_or_create_category(self, category_name):
        category = self.env["product.category"].search([("name", "=", category_name)], limit=1)
        if not category:
            category = self.env["product.category"].create(
                {
                    "parent_id": self.env.ref("product.product_category_all").id,
                    "name": category_name,
                }
            )
        return category

    def _create_or_update_product(self, row, category):
        product_tmpl_vals = {
            "name": row["Product Name"],
            "type": "product",
            "categ_id": category.id,
            "list_price": row["Price"],
        }
        product_tmpl = self.env["product.template"].search(
            [("name", "=", product_tmpl_vals["name"])], limit=1
        )
        if product_tmpl:
            product_tmpl.write(product_tmpl_vals)
        else:
            product_tmpl = self.env["product.template"].create(product_tmpl_vals)
        return product_tmpl

    def _update_product_quantity(self, product_tmpl, product_quantity):
        if product_tmpl.qty_available != product_quantity:
            inventory_wizard = self.env["stock.change.product.qty"].create(
                {
                    "product_id": product_tmpl.product_variant_id.id,
                    "product_tmpl_id": product_tmpl.id,
                    "new_quantity": product_quantity,
                }
            )
            inventory_wizard.change_product_qty()

    def import_file(self):
        df = self._decode_file_content()
        for _, row in df.iterrows():
            category = self._find_or_create_category(row["Category"])
            product_tmpl = self._create_or_update_product(row, category)
            self._update_product_quantity(product_tmpl, row["Quantity"])
