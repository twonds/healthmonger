import time

from behave import *  # noqa

from integration.lib import api

@given(u'a client') # noqa
def step_impl(context):
    context.client = api.create()
    # wait for running server
    for i in range(5):
        try:
            status = context.client.status()
            if status == "OK":
                break
        except:
            pass
        time.sleep(0.5)

@when(u'the client makes a status request')
def step_impl(context):
    context.client.status()

@then(u'the status is {status}')
def step_impl(context, status):
    assert(context.client.server_status == status)

@when(u'the client makes a load data request.') # noqa
def step_impl(context):
    r = context.client.load_data()
    assert(r.status_code == 200)
    context.client.data_loaded = r.json()

@then(u'the client can observe that data is loaded.') # noqa
def step_impl(context):
    data_loaded_result = getattr(context.client, 'data_loaded', {})
    assert('loaded' == data_loaded_result.get('status', 'error'))

@when(u'the client queries "{table}" for "{attribute}" returning all "{values}"')  # noqa
def step_impl(context, table, attribute, values):
    context.client.query(table, attribute, values)
    raise NotImplementedError(u'STEP: When the client queries "{0}" for "{1}" returning all "{2}"'.format(table, attribute, values))  # noqa

@then(u'from "{table}" the "{attribute}" value is "{check}"')
def step_impl(context, table, attribute, check):
    raise NotImplementedError(u'STEP: Then from {0} the "{1}" value is "{2}"'.format(table, attribute, check)) # noqa
