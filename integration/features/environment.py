from collections import defaultdict

def before_scenario(context, _):
    context.results = defaultdict(list)
