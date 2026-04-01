def main():
    import argparse
    from jinja2 import Environment, FileSystemLoader
    from weasyprint import HTML
    from datetime import datetime
    import calendar
    import json

    parser = argparse.ArgumentParser(
        description="PDF invoice generator"
    )

    parser.add_argument(
        "--data-ref-file",
        default="data.example.json",
        help="JSON file name inside data_refs/"
    )

    parser.add_argument(
        "--template-file",
        default="spanish.jinja.html",
        help="Template file name inside template/"
    )

    parser.add_argument(
        "--start-month",
        type=int,
        default=4,
        choices=range(1, 13),
        help="Starting month number (1-12), default is 4 (April). Generates invoices to December."
    )

    args = parser.parse_args()

    DATA_REF_FILE = args.data_ref_file
    TEMPLATE_FILE = args.template_file
    START_MONTH = args.start_month

    with open(f"data_refs/{DATA_REF_FILE}") as f_obj:
        data_ref = f_obj.read()

    data_ref = json.loads(data_ref)


    data_invoices = []
    for i, n in enumerate(range(START_MONTH, 13)):
        date_month = datetime(data_ref["INVOICE_YEAR"], n, 1)
        last_day_month = date_month.replace(
            day=calendar.monthrange(date_month.year, date_month.month)[1]
        )
        base_value = float(data_ref["INVOICE_BASE"])
        iva_quantity = base_value * float(data_ref["INVOICE_IVA_PERCENTAGE"])
        retention_quantity = base_value * float(data_ref["INVOICE_RETENTION_PERCENTAGE"])
        total_quantity = base_value + iva_quantity + retention_quantity

        data_invoices.append(
            {
                **data_ref,
                "INVOICE_NUMBER": i+1,
                "INVOICE_DATE": date_month.strftime("%d/%m/%Y"),
                "INVOICE_LAST_DATE" : last_day_month,
                "INVOICE_CONCEPT_ENRICHED": f"{data_ref['INVOICE_CONCEPT']}<br>{date_month.strftime('%d/%m/%Y')} - {last_day_month.strftime('%d/%m/%Y')}",

                "INVOICE_BASE": f"{base_value:.2f}",
                "INVOICE_IVA_QUANTITY": f"{iva_quantity:.2f}",
                "INVOICE_RETENTION_QUANTITY": f"{retention_quantity:.2f}",
                "INVOICE_TOTAL_QUANTITY": f"{total_quantity:.2f}"
            }
        )

    TEMPLATE_DIR = "./template"

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)


    for data in data_invoices:
        html_out = template.render(**data)           

        output_file = f"invoices/invoice_{data['CUSTOMER_ALIAS']}_{data['INVOICE_LAST_DATE'].strftime('%m%Y')}.pdf"
        HTML(string=html_out).write_pdf(output_file)

        print(f"Invoice generated: {output_file}")


if __name__ == "__main__":
    main()
