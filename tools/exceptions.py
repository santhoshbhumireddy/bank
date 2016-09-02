"""Exception classes of application"""


class AppError(Exception):
    """Base exception class for the application"""


class AuthError(AppError):
    """Application authentication error"""


class NoRecordFoundError(AppError):
    """Record doesn't exist in DB"""
    def __init__(self, rec_name, rec_id):
        msg = '%(rec_name)s with id %(rec_id)s doesn\'t exist in DB' % \
              dict(rec_name=rec_name, rec_id=rec_id)
        super(NoRecordFoundError, self).__init__(msg)


class ReadOnlyError(AppError):
    """Exception for edit disabled entities"""
    def __init__(self, campaign_id, object_type='campaign'):
        msg = "Can't change {0} {1}. It may be a production {1}.".\
            format(campaign_id, object_type)
        super(ReadOnlyError, self).__init__(msg)


class DBOperationError(AppError):
    """Parent class for errors related to DB processing"""


class InvalidColumnError(DBOperationError):
    """Requested Column is invalid"""
    def __init__(self, table, column):
        msg = 'Table %s doesn\'t have column %s' % (table, column)
        super(InvalidColumnError, self).__init__(msg)


class InvalidExchangeError(AppError):
    """Exchange is invalid"""


class InvalidInputError(AppError):
    """Invalid input error"""


class NoDataError(AppError):
    """Generic exception for data not found related errors"""


class NoDBFoundError(AppError):
    """DB doesn't exist error"""


class ServiceError(AppError):
    """Generic exception class for service related errors"""


class ServiceAuthError(ServiceError):
    """Generic exception class for service authentication related errors"""


class SimultaneousEditError(AppError):
    """Exception class for simultaneous edit error"""


CAMPAIGN_CREATE_ERROR = 'Error while creating campaign'
