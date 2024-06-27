import base64
from io import BytesIO

import pandas as pd

from odoo import fields, models
from odoo.exceptions import ValidationError


class ProductImportWizard(models.TransientModel):
    _name = "product.import.wizard"
    _description = "Product Import Wizard"

    data_file = fields.Binary("Excel File", required=True)

    def import_file(self):
        """
        Imports and processes an Excel file to create or update products in the system.
        """
        file_content = base64.b64decode(self.data_file)
        file_stream = BytesIO(file_content)
        df = pd.read_excel(file_stream, engine="openpyxl")

        # check missing columns
        missing_columns = []
        for column in ["Category", "Product Name", "Price", "Quantity"]:
            if column not in df.columns:
                missing_columns.append(column)
        if missing_columns:
            raise ValidationError(f"Missing columns in Excel file: {', '.join(missing_columns)}")

        for _, row in df.iterrows():
            category_name = row["Category"]
            product_name = row["Product Name"]
            product_price = row["Price"]
            product_quantity = row["Quantity"]

            # create find or create product category
            category = self.env["product.category"].search([("name", "=", category_name)], limit=1)
            if not category:
                category = self.env["product.category"].create(
                    {
                        "parent_id": self.env.ref("product.product_category_all").id,
                        "name": category_name,
                    }
                )

            # create or update product
            product_tmpl_vals = {
                "name": product_name,
                "type": "product",
                "categ_id": category.id,
                "list_price": product_price,
            }
            product_tmpl = self.env["product.template"].search(
                [("name", "=", product_name)], limit=1
            )
            if product_tmpl:
                product_tmpl.write(product_tmpl_vals)
            else:
                product_tmpl = self.env["product.template"].create(product_tmpl_vals)

            # update product quantity
            if product_tmpl.qty_available != product_quantity:
                inventory_wizard = self.env["stock.change.product.qty"].create(
                    {
                        "product_id": product_tmpl.product_variant_id.id,
                        "product_tmpl_id": product_tmpl.id,
                        "new_quantity": product_quantity,
                    }
                )
                inventory_wizard.change_product_qty()
