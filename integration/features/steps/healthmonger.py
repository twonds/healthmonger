import time

from behave import *  # noqa

from integration.lib import api

@given(u'a client') # noqa
def step_impl(context):
    context.client = api.create()
    # wait for running server
    for i in range(10):
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
    result = context.client.query(table, attribute, values)
    context.results[table].append(result)

@then(u'from the "{table}" result the "{key}" value is greater than "{value}"')
def step_impl(context, table, key, value):
    def check(check_val):
        assert(int(check_val) > int(value))
    check_results(context, table, key, check)

@then(u'from the "{table}" result the "{key}" value is {value}')
def step_impl(context, table, key, value):
    def check(check_val):
        print(check_val)
        if value == "undefined":
            assert(check_val is None)
        else:
            # XXX - check types and convert
            assert(int(check_val) == int(value))

    check_results(context, table, key, check)

@then(u'the "{table}" result is empty')
def step_impl(context, table):
    q_result = context.results[table][0]
    results = q_result.get('results', [])
    assert(not results)

@then(u'the "{table}" result is an error')
def step_impl(context, table):
    q_result = context.results[table][0]
    assert('error' in q_result)

def check_results(context, table, key, f):
    # Check all returned rows
    for row in fetch_results(context, table):
        check_val = row.get(key)
        f(check_val)

def fetch_results(context, table):
    q_result = context.results[table][0]
    results = q_result.get('results', [])
    assert(results != [])
    return results
