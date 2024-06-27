import base64

from odoo.modules.module import get_module_resource
from odoo.tests.common import Form, TransactionCase


class TestProductImport(TransactionCase):
    def test_import_products(self):
        """
        Verify import products and categories from Excel file.
        1. Load a sample file containing products and categories.
        2. Perform the import using a wizard.
        3. Check if the products have been imported correctly.
        """
        # load the sample Excel file
        file_path = get_module_resource(
            "tech_gear_inventory", "tests", "data", "products_data.xlsx"
        )
        with open(file_path, "rb") as f:
            data_file = base64.b64encode(f.read())
            with Form(self.env["product.import.wizard"]) as wizard_form:
                wizard_form.data_file = data_file
            wizard_form.save()
            wizard = wizard_form.save()

            # run the import
            wizard.import_file()

        # check if the product have been imported correctly
        product_tmpl = self.env["product.template"].search(
            [("name", "=", "Samsung SM-A057 Galaxy")], limit=1
        )
        self.assertTrue(product_tmpl)
        self.assertEqual(product_tmpl.list_price, 165.0)
        self.assertEqual(product_tmpl.qty_available, 15)
        self.assertEqual(product_tmpl.categ_id.name, "Mobiles")

        # reset values
        product_tmpl.list_price = 1
        product_tmpl.qty_available = 1
        product_tmpl.categ_id = False
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": product_tmpl.product_variant_id.id,
                "product_tmpl_id": product_tmpl.id,
                "new_quantity": 0,
            }
        )
        inventory_wizard.change_product_qty()
        self.assertEqual(product_tmpl.qty_available, 0)

        # import again
        wizard.import_file()

        # the values are updated after second import
        self.assertEqual(product_tmpl.list_price, 165.0)
        self.assertEqual(product_tmpl.qty_available, 15)
        self.assertEqual(product_tmpl.categ_id.name, "Mobiles")
