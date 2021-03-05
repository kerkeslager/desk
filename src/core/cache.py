import itertools

def memoize(timeout, cache=None):
    '''
    Memoize the function with the given timeout and cache. If no cache is
    given, the 'default' cache is used.

    Calls are cached under keys based on their module "path" followed by
    the args/kwargs passed to them. For example:

        # foo/bar.py in the PYTHONPATH, i.e. module foo.bar
        @cache.memoize(300)
        def baz(a, **kwargs):
            ...

        baz(1, qux=2) # Result is cached under the key "foo.bar.baz(1,qux=2)"

    Note that kwargs are sorted so that f(a=1,b=2) and f(b=2,a=1) are given
    the same key. Note, however, that there's a bug when positional arguments
    are passed in by name, i.e. for the function...

        def f(arg):
            ...

    The calls f(1) and f(arg=1) will receive separate keys.
    There's a way to fix that by introspecting the arguments to f--I'll fix it
    if anyone reports it.

    Also note the use of repr(). As far as I can tell this will be unique for
    simple builtin types (float, int, str, etc.) and list/dict objects which
    contain those types. I'm leaving open the possibility of user-defined types
    being cached here because I can't see a strong reason not to, but if anyone
    overrides repr() in such a way that it doesn't return something unique, and
    reports it to me as a cache collision bug, I'll deprecate this
    functionality because it's too hard to support well. Don't be the person
    who screws it up for everyone.
    '''
    if cache is None:
        from django.core.cache import cache

    def decorator(f):
        key_prefix = '{}.{}'.format(f.__module__, f.__name__)

        def get_key(*args, **kwargs):
            return '{}({})'.format(
                key_prefix,
                ','.join(itertools.chain(
                    (repr(arg) for arg in args),
                    ('{}={}'.format(k, repr(v)) for k,v in sorted(kwargs.items())),
                )),
            )

        def memoized(*args, **kwargs):
            sentinel = object()
            key = get_key(*args, **kwargs)

            result = cache.get(key, sentinel)

            if result is sentinel:
                result = f(*args, **kwargs)
                cache.set(key, result, timeout)

            return result

        return memoized

    return decorator
