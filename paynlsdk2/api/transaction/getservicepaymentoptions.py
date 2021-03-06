import json

from marshmallow import Schema, fields, pre_load, post_load

from paynlsdk2.api.requestbase import RequestBase
from paynlsdk2.api.responsebase import ResponseBase
from paynlsdk2.objects import ErrorSchema, Merchant, MerchantSchema, Service, ServiceSchema,\
    PaymentOption, PaymentOptionSchema, CountryOption, CountryOptionSchema,\
    ServicePaymentProfile, ServicePaymentProfileSchema
from paynlsdk2.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Transaction::getservicepaymentoptions API

    :param Merchant merchant: Merchant details
    :param Service merchant: Service details
    :param dict settings: any relevant settings (key/value)
    :param country_options Dict[str, CountryOption]: country options
    :param payment_profiles Dict[str, ServicePaymentProfile]: payment profile info
    """
    def __init__(self,
                 merchant=None,
                 service=None,
                 settings=None,
                 # payment_options=None,
                 country_options=None,
                 payment_profiles=None,
                 *args, **kwargs):
        # type: (Merchant, Service, dict, Dict[str, CountryOption], Dict[str, ServicePaymentProfile]) -> None
        self.merchant = merchant
        self.service = service
        self.settings = settings
        # self.payment_options = payment_options
        self.country_options = country_options
        self.payment_profiles = payment_profiles
        super(Response, self).__init__(**kwargs)

    def __repr__(self):
        # type: () -> str
        return self.__dict__.__str__()


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)
    merchant = fields.Nested(MerchantSchema, required=False)
    service = fields.Nested(ServiceSchema, required=False)
    settings = fields.Dict(required=False, allow_none=True)
    payment_options = fields.List(fields.Nested(PaymentOptionSchema), required=False, load_from='paymentOptions')
    country_options = fields.List(fields.Nested(CountryOptionSchema), required=False, load_from='countryOptionList')
    payment_profiles = fields.List(fields.Nested(ServicePaymentProfileSchema), required=False, load_from='paymentProfiles')

    @pre_load
    def pre_processor(self, data):
        # type: (dict) -> dict
        #  API might return empty string instead of dictionary object
        if ParamValidator.is_empty(data['settings']):
            del data['settings']
        #  API might return empty string instead of dictionary object
        if ParamValidator.is_empty(data['paymentOptions']):
                del data['paymentOptions']
        elif 'paymentOptions' in data and ParamValidator.not_empty(data['paymentOptions']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['paymentOptions'].items():
                list.append(item)
            data['paymentOptions'] = list
        #  API might return empty string instead of dictionary object
        if ParamValidator.is_empty(data['countryOptionList']):
            del data['countryOptionList']
        elif 'countryOptionList' in data and ParamValidator.not_empty(data['countryOptionList']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['countryOptionList'].items():
                list.append(item)
            data['countryOptionList'] = list
        #  API might return empty string instead of dictionary object
        if 'paymentProfiles' in data and ParamValidator.is_empty(data['paymentProfiles']):
            del data['paymentProfiles']
        elif 'paymentProfiles' in data and ParamValidator.not_empty(data['paymentProfiles']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['paymentProfiles'].items():
                list.append(item)
            data['paymentProfiles'] = list
        return data

    @post_load
    def create_response(self, data):
        # type: (dict) -> Response
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo preprocessing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'payment_options' in data:
            rs = {}
            for item in data['payment_options']:
                rs[item.id] = item
            data['payment_options'] = rs
        if 'country_options' in data:
            rs = {}
            for item in data['country_options']:
                rs[item.id] = item
            data['country_options'] = rs
        if 'payment_profiles' in data:
            rs = {}
            for item in data['payment_profiles']:
                rs[item.id] = item
            data['payment_profiles'] = rs
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Transaction::getservicepaymentoptions API

    :param str payment_method_id: Payment method ID
    """
    def __init__(self, payment_method_id=None):
        # type: (str) -> None
        self.payment_method_id = payment_method_id
        super(Request, self).__init__()

    def requires_api_token(self):
        # type: () -> bool
        return True

    def requires_service_id(self):
        # type: () -> bool
        return True

    def get_version(self):
        # type: () -> int
        return 12

    def get_controller(self):
        # type: () -> str
        return 'Transaction'

    def get_method(self):
        # type: () -> str
        return 'getServicePaymentOptions'

    def get_query_string(self):
        # type: () -> str
        return ''

    def get_parameters(self):
        # type: () -> dict
        # Get default api parameters
        rs = self.get_std_parameters()
        # Add own parameters
        if ParamValidator.not_empty(self.payment_method_id):
            rs['paymentMethodId'] = self.payment_method_id
        return rs

    @RequestBase.raw_response.setter
    def raw_response(self, raw_response):
        self._raw_response = raw_response
        # Do error checking.
        rs = json.loads(self.raw_response)
        schema = ResponseSchema(partial=True)
        response, errors = schema.load(rs)
        self.handle_schema_errors(errors)
        self._response = response

    @property
    def response(self):
        # type: () -> Response
        """
        Return the API :class:`Response` for the validation request

        :return: The API response
        :rtype: paynlsdk2.api.transaction.getservicepaymentoptions.Response
        """
        return self._response

    @response.setter
    def response(self, response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

