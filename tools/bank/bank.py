#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Storing account and transaction related information in database.

@created: 21-Apr-2016
@author: Santosh Reddy Bhumireddy
@mail: santhoshbhumireddy@gmail.com
"""
import json
import os


import settings

from tools.exceptions import DBOperationError, InvalidInputError
from tools.log import logger
from tools.models import Account, Payee, Transaction
from tools.services.db_api import DatabaseAPI
from tools.utils import random_with_N_digits, encode


class AccountBuilder(object):
    """Basic layer for Account Info"""

    @staticmethod
    def create_or_edit(data, user, account_id=None):
        """Create the account info"""
        try:
            account_info = data['account_info']
        except Exception:
            raise InvalidInputError('Invalid Json')
        try:
            account = Account()
            account.from_dict(account_info)
            with DatabaseAPI() as db_obj:
                if account_id:
                    account.id = account_id
                    account_obj = db_obj.get_obj(Account, account_id)
                account.user_id = user.id
                account.account_id = user.account_id
                account.account_name = user.user_name
                account_id = db_obj.insert_or_update(account, 'id')
                return {"account": {"id": account_id}}
        except Exception as e:
            raise DBOperationError(e.message)


    @staticmethod
    def fetch(id):
        """Fetches Account info"""
        with DatabaseAPI() as db_obj:
            account = db_obj.get_obj(Account, account_id=id)
        del account._sa_instance_state
        account = dict(account)
        return {'account': account}

    @staticmethod
    def fetch_all():
        """Fetches all Accounts info"""
        with DatabaseAPI() as db_obj:
            accounts = db_obj.get_objs(Account)
            if accounts:
                return {'accounts': [dict(account) for account in accounts]}
            else:
                return {'accounts': []}

    @staticmethod
    def delete(id):
        """Delete Account"""
        with DatabaseAPI() as db_obj:
            db_obj.del_obj(Account, account_id=id)
        return


class TransactionBuilder(object):
    """Basic layer for Transaction"""
    @staticmethod
    def create_or_edit(data, user, transaction_id=None):
        """Make the Transaction"""
        try:
            transaction_info = data['transaction_info']
        except Exception:
            raise InvalidInputError('Invalid Json')
        try:
            transaction = Transaction()
            # transaction.from_dict(transaction_info)
            src_account_id = transaction_info.get('src_account_id')
            dst_account_id = transaction_info.get('dst_account_id', None)
            transaction_type = transaction_info['transaction_type']
            if transaction_type == 'Deposit':
                type = 'DEPOSITED'
            else:
                type = 'CREDITED'
            transaction_amount =  float(transaction_info['amount'])
            description = transaction_info.get('description', '')
            with DatabaseAPI() as db_obj:
                if transaction_id:
                    transaction.id = transaction_id
                    transaction_obj = db_obj.get_obj(Transaction, transaction_id)
                src_account_obj = db_obj.get_obj(Account, account_id=src_account_id)
                if type == 'CREDITED':
                    transaction_password = transaction_info.get('transaction_password', None)
                    if transaction_password:
                        transaction_password_hash = encode(settings.ENCRYPTION_KEY, transaction_password)
                        if user.transaction_password_hash != transaction_password_hash:
                            raise InvalidInputError('Invalid Transaction password')
                    else:
                        raise InvalidInputError('Transaction password is needed to withdraw and transfer money')
                    if transaction_amount > src_account_obj.balance:
                        raise InvalidInputError('Insufficient Balance')
                if transaction_type == 'ThirdParty':
                    if dst_account_id:
                        dst_account_obj = db_obj.get_obj(Account, account_id=dst_account_id)
                        if not dst_account_obj:
                            raise InvalidInputError(
                                'Third Party payee account id is not existed')
                        src_account_obj.balance -= transaction_amount
                        dst_account_obj.balance += transaction_amount
                        description += ' Funds transfered to: ' + dst_account_id
                    else:
                        raise InvalidInputError('Third Party payee account id is needed to transfer money third party payee')
                elif type == 'DEPOSITED':
                    src_account_obj.balance += transaction_amount
                    description = "Deposited: " + description
                else:
                    src_account_obj.balance -= transaction_amount
                    description = "Credited: " + description

                transaction_id = random_with_N_digits(12)
                transaction.transaction_id = str(transaction_id)
                transaction.account_id = src_account_id
                transaction.type = type
                transaction.description = description
                transaction.amount = transaction_amount
                transaction.total = src_account_obj.balance

                db_obj.insert_or_update(src_account_obj)
                db_obj.insert_or_update(transaction)

                if transaction_type == 'ThirdParty':
                    db_obj.insert_or_update(dst_account_obj)
                    transaction_id = random_with_N_digits(12)
                    transaction.transaction_id = str(transaction_id)
                    transaction.account_id = dst_account_id
                    transaction.type = 'DEPOSITED'
                    transaction.description = transaction_info.get('description', '') + ' Funds came from: ' + src_account_id
                    transaction.amount = transaction_amount
                    transaction.total = dst_account_obj.balance
                    db_obj.insert_or_update(transaction)
                return {"transaction": {"id": transaction_id}}
        except Exception as e:
            raise DBOperationError(e.message)

    @staticmethod
    def fetch(id):
        """Fetches transaction info"""
        with DatabaseAPI() as db_obj:
            transaction = db_obj.get_obj(Transaction, id=id)
        return {'transaction': dict(transaction)}

    @staticmethod
    def fetch_all(**query_params):
        """Fetches all transactions"""
        with DatabaseAPI() as db_obj:
            transactions = db_obj.get_objs(Transaction, **query_params)
            if transactions:
                return {'transactions': [dict(transaction) for transaction in transactions]}
            else:
                return {'transactions': []}

    @staticmethod
    def delete(id):
        """Delete Transaction info"""
        with DatabaseAPI() as db_obj:
            db_obj.del_obj(Transaction, id=id)
        resp = {"status": "ok"}
        return resp

class PayeeBuilder(object):
    """Basic layer for Payees"""
    @staticmethod
    def create_or_edit(data, user, payee_id=None):
        """Creates or edits the Payee"""
        try:
            payee_info = data['payee_info']
        except Exception:
            raise InvalidInputError('Invalid Json')
        try:
            payee = Payee()
            payee.from_dict(payee_info)
            with DatabaseAPI() as db_obj:
                if payee_id:
                    payee.id = payee_id
                    payee_obj = db_obj.get_obj(Payee, payee_id)
                payee.user_id = user.id
                payee_id = db_obj.insert_or_update(payee, 'id')
                return {"payee": {"id": payee_id}}
        except Exception as e:
            raise DBOperationError(e.message)

    @staticmethod
    def fetch(id):
        """Fetches Payee info"""
        with DatabaseAPI() as db_obj:
            payee = db_obj.get_obj(Payee, id=id)
        return {'payee': dict(payee)}

    @staticmethod
    def fetch_all(**query_params):
        """Fetches all Payees"""
        with DatabaseAPI() as db_obj:
            payees = db_obj.get_objs(Payee, **query_params)
            if payees:
                return {'payees': [dict(payee) for payee in payees]}
            else:
                return {'payees': []}

    @staticmethod
    def delete(id):
        """Delete Payee"""
        with DatabaseAPI() as db_obj:
            db_obj.del_obj(Payee, id=id)
        resp = {"status": "ok"}
        return resp