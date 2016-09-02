#!/usr/bin/python

"""Handlers for Bank Application"""

# Library Imports
import json

# Application Imports
from handlers.base import BaseHandler
from tools.bank.bank import AccountBuilder, PayeeBuilder, TransactionBuilder

class Accounts(BaseHandler):
    """Handler for Accounts"""

    def prepare(self):
        super(Accounts, self).prepare()
        self.account_obj = AccountBuilder()

    def get(self):
        query_params = self.get_query_argument('query_params', None)
        if query_params:
            return self.account_obj.fetch_all(**json.loads(query_params))
        else:
            return self.account_obj.fetch_all()

    def post(self):
        return self.account_obj.create_or_edit(
            self.request.body, self.current_user)


class AccountInfo(BaseHandler):
    """Handler for Account Info"""

    def prepare(self):
        super(AccountInfo, self).prepare()
        self.account_obj = AccountBuilder()

    def get(self, account_id):
        return self.account_obj.fetch(account_id)

    def put(self, account_id):
        return self.account_obj.create_or_edit(
            self.request.body, self.current_user, account_id)

    def delete(self, account_id):
        return self.account_obj.delete(account_id)

class Payees(BaseHandler):
    """Handler for Payees"""

    def prepare(self):
        super(Payees, self).prepare()
        self.payee_obj = PayeeBuilder()

    def get(self):
        query_params = self.get_query_argument('query_params', None)
        if query_params:
            return self.payee_obj.fetch_all(**json.loads(query_params))
        else:
            return self.payee_obj.fetch_all()

    def post(self):
        return self.payee_obj.create_or_edit(
            self.request.body, self.current_user)


class PayeeInfo(BaseHandler):
    """Handler for Payee"""

    def prepare(self):
        super(PayeeInfo, self).prepare()
        self.payee_obj = PayeeBuilder()

    def get(self, payee_id):
        return self.payee_obj.fetch(payee_id)

    def put(self, payee_id):
        return self.payee_obj.create_or_edit(
            self.request.body, self.current_user, payee_id)

    def delete(self, payee_id):
        return self.payee_obj.delete(payee_id)


class Transactions(BaseHandler):
    """Handler for Transactions"""

    def prepare(self):
        super(Transactions, self).prepare()
        self.transaction_obj = TransactionBuilder()

    def get(self):
        query_params = self.get_query_argument('query_params', None)
        if query_params:
            return self.transaction_obj.fetch_all(**json.loads(query_params))
        else:
            return self.transaction_obj.fetch_all()

    def post(self):
        return self.transaction_obj.create_or_edit(
            self.request.body, self.current_user)


class TransactionInfo(BaseHandler):
    """Handler for Transaction"""

    def prepare(self):
        super(TransactionInfo, self).prepare()
        self.transaction_obj = TransactionBuilder()

    def get(self, transaction_id):
        return self.transaction_obj.fetch(transaction_id)

    def put(self, transaction_id):
        return self.transaction_obj.create_or_edit(
            self.request.body, self.current_user, transaction_id)

    def delete(self, transaction_id):
        return self.transaction_obj.delete(transaction_id)


handlers = [
    (r'/accounts', Accounts),
    (r'/account/(\d+)', AccountInfo),
    (r'/payees', Payees),
    (r'/payee/(\d+)', PayeeInfo),
    (r'/transactions', Transactions),
    (r'/transaction/(\d+)', TransactionInfo),
]


if __name__ == "__main__":
    pass
