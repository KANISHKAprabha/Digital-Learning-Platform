

class BookingError(Exception):
    pass
class ParentNotFoundError(Exception):
    pass
class LSANotFoundError(Exception):
    pass

class LSANotActiveError(Exception):
    pass
class SkillMisMatchError(Exception):
    pass
class LSAUnavailableError(Exception):
    pass



class PaymentNotFoundError(Exception):
    pass

class InvalidPaymentTransactionError(Exception):
    pass
