#!/usr/bin/env python3
import calendar
from datetime import date
from decimal import Decimal
import json
import os
import subprocess

from argparse import ArgumentParser
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from jinja2 import Environment, select_autoescape
from jinja2.loaders import FileSystemLoader

__author__ = "Simone Pandolfi <simopandolfi@gmail.com>"
__version__ = 1


BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

ENV: Environment = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates'), 
                            followlinks=True), 
    autoescape=select_autoescape(['html', 'xml'])
)


def last_month() -> tuple:
    today = date.today()
    month = today.month - 1 if today.month > 1 else 12
    year = today.year if today.month > 1 else today.year - 1
    weekday, ndays = calendar.monthrange(year, month)
    return (date(year, month, 1),
    date(year, month, ndays))


start_date, end_date = last_month()


ARGS_PARSER: ArgumentParser = ArgumentParser(description='Invoice generator')
ARGS_PARSER.add_argument('settings', help='Settings file')
ARGS_PARSER.add_argument('invoice_number', metavar='n', help='Invoice number')
ARGS_PARSER.add_argument('--issue-date', dest='issue_date', 
                         type=lambda x: parse(x).date(),
                         default=date.today(),
                         help='Issue date (default: today)')
ARGS_PARSER.add_argument('--expiry', dest='expiry', type=int, default=30, \
                         help='Expiration days')
ARGS_PARSER.add_argument('--start-date', dest='start_date', 
                         type=lambda x: parse(x).date(),
                         default=start_date,
                         help='Start working date (default: the 1st day of the \
                              precending month)')
ARGS_PARSER.add_argument('--end-date', dest='end_date', 
                         type=lambda x: parse(x).date(),
                         default=end_date,
                         help='End working date (default: the last day of the \
                              precending month)')


if __name__ == '__main__':
    args = ARGS_PARSER.parse_args()

    with open(args.settings, 'r') as fp:
        context = json.load(fp)
    context['invoice_number'] = args.invoice_number
    context['start_date'] = args.start_date
    context['end_date'] = args.end_date
    context['issue_date'] = args.issue_date
    context['due_date'] = context['issue_date'] + relativedelta(
        days=args.expiry)
    context['consultant']['fee'] = Decimal(context['consultant']['fee'])
    context['vat'] = Decimal(context['vat'])
    context['withholding_tax'] = Decimal(context['withholding_tax'])
    context['national_pension_fund'] = Decimal(context['national_pension_fund'])
    context['national_pension_fund_value'] = \
        context['consultant']['fee'] * context['national_pension_fund'] / \
        Decimal(100)
    context['total_taxable_amount'] = context['consultant']['fee'] + \
        context['national_pension_fund_value']
    context['vat_value'] = context['total_taxable_amount'] * context['vat'] / \
        Decimal(100)
    context['invoice_total'] = context['total_taxable_amount'] + \
        context['vat_value']
    context['withholding_tax_value'] = \
        context['total_taxable_amount'] * context['withholding_tax'] / \
        Decimal(100)
    context['due'] = context['invoice_total'] - context['withholding_tax_value']

    template = ENV.get_template('invoice.html')
    filename = '{0}_{1}_{2}'.format(
        context['invoice_number'], 
        context['issue_date'].strftime("%d/%m/%Y").replace('/', '-'), 
        context['company']['name'].replace(' ', '_').replace('.', '')
    )
    with open(os.path.join('invoices', '{0}.html'.format(filename)), 'w') as fp:
        fp.write(template.render(context))
    
    # starts a simple HTTP server
    http_proc = subprocess.Popen(['python', '-m', 'http.server', '8033'])

    # starts chrome headless
    chrome_proc = subprocess.Popen([
        'chrome', '--headless', '--disable-gpu', '--print-to-pdf', 
        'http://localhost:8033/invoices/{0}.html'.format(filename)
    ])
    
    chrome_proc.wait()
    http_proc.terminate()

    os.rename('output.pdf', 
              os.path.join('invoices', '{0}.pdf'.format(filename)))
    os.remove(os.path.join('invoices', '{0}.html'.format(filename)))
