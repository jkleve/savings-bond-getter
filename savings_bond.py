#!/bin/env python3

"""
 Requirements:
    BeatifulSoup
    lxml
"""

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
from collections import namedtuple
from requests import post

"""
Bond:
    Input - Stores data about the bond for post request to Treasury Direct
BondData
    Output - Stores data received from post request to Treasury Direct
"""
Bond = namedtuple("Bond", "serial type amount issue_date date")
BondData = namedtuple("BondData", "serial series denom issue_date next_accrual final_maturity issue_price "
                                  "interest interest_rate value")


def extract_bond_data(html):
    """Extract the bond's data from the html"""
    soup = BeautifulSoup(html, 'lxml')
    table = soup.body.find('table', attrs={'class': 'bnddata'})

    row = table.find_all("tr")[1]
    data = list(td.get_text() for td in row.find_all("td"))

    bond = BondData(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9])

    return bond


def post_bond_to_treasury_direct(bond):
    """Send a post request to Treasury Direct with the parameters in the bond"""
    url = "https://www.treasurydirect.gov/BC/SBCPrice"
    params = {'RedemptionDate': bond.date, 'Series': bond.type, 'SerialNumber': bond.serial,
              'IssueDate': bond.issue_date, 'Denomination': bond.amount, 'btnAdd.x': 'CALCULATE'}
    r = post(url, data=params)
    if r.status_code == 200:
        return r.text
    else:
        raise Exception("Bad Post Response.")


table_format_str = "{:10} {:6} {:6} {:10} {:11} {:13} {:10} {:8} {:12} {:5}"


def print_bond(bond):
    """Print the bond"""
    print(table_format_str.format(bond.serial, bond.series, bond.denom, bond.issue_date,
                                              bond.next_accrual, bond.final_maturity,
                                              bond.issue_price, bond.interest,
                                              bond.interest_rate, bond.value))


# TODO implement sort key
def print_bonds(bonds, sort_key=None):
    """Print header and then iterate through each bond calling print_bond"""
    print(table_format_str.format("Serial", "Series", "Denom", "IssueDate", "NextAccrual",
                                              "FinalMaturity", "IssuePrice", "Interest",
                                              "InterestRate", "Value"))
    for bond in bonds:
        print_bond(bond)


def print_total(bonds):
    """Print the total of all bonds"""
    total = 0.0
    for bond in bonds:
        amount = bond.value.strip('$')
        total += float(amount)
    print('-------------------------------------------------------------------------------------------------------')
    print('Total                                                                                          ${}'
          .format(total))


if __name__ == "__main__":
    from bonds import list_of_bonds
    """
    To protect the private information of my bonds, I've stored them in a separate file
    called bonds.py. You can see a template of this file below. You can either copy this
    template into bonds.py in this same directory and update the information to your bonds or
    you can comment in the lines here.

    bonds.py:
    -----------------------------
    from savings_bond import Bond
    from time import strftime

    today = strftime("%m/%Y")
    list_of_bonds = list((Bond('xxxxxxxxxx', 'EE', 50, '01/2000', today),
                          Bond('yyyyyyyyyy', 'EE', 50, '02/2003', today),
                          Bond('zzzzzzzzzz', 'EE', 200, '03/2011', today),
    """

    bond_data = list()
    for bond in list_of_bonds:
        html = post_bond_to_treasury_direct(bond)
        data = extract_bond_data(html)
        bond_data.append(data)

    print_bonds(bond_data)
    print_total(bond_data)
