from webdrivers.webhelper import WebHelper

class IllegalArgumentError(ValueError):
    pass


class BrowserWebElementMissingError(WebHelper.NoSuchElementException):
    pass


class ExpectedDataNotFoundException(ValueError):
    pass


class NoneResponseException(ValueError):
    pass
