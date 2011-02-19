from adapter import BaseAdapter

class InterfaceClass(object):
    """ InterfaceClass is responsible for handling
        the component registry for each interface.
    """

    """ NOTE: context can be a dict for multi-adapters
        possibly more manageable than zope style?
    """

    """ Class-level operations """

    def __init__(self, name, bases=(),
                 attrs=None, __doc__=None, __module__=None):
        """ Setup the registry. 

            Upon construction, accept class meta-data relating
            to the derived Interface and store.
        """

        self.name = name

        """ Init a dict to store class/ruleset
            key/value pairs
        """
        self.__registry = {}

    def __call__(self, context=None):
        """ Return a component implementing Interface for @context.

            Component can be one of the following:
            - A single component
            - An adapter/multi-adapter
            - A generator of subscribed components
        """
        component = self.lookup(context)

        """ If an adapter is returned, initialise it """
        if issubclass(component, BaseAdapter):
            return component(context)

        return component

    """ Component Registration """

    def register(self, cls, ruleset=None):
        """ Register component for Interface.

            An optional @ruleset helps the registry return
            the most relevant component.

            @cls is the class that should be registered.

            @ruleset can be any callable that returns a
            boolean value. Rulesets are evaluated for their specificity
            which is used in conjuction with the specifity of the Interfaces
            involved in the request.

            Functions have a specificity of 1, whilst RuleSet classes/instances
            have a specificity equal to the number of predicates they implement

            It is also possible to boost RuleSets which takes effect only if there are more
            than one potential candidates with equal specificity ratings.
            Can be used as a decorator:
                @MyInterface.register
                class MyComponent(object):
                    pass

        """

        """ @registry is a dict where the key is cls and
            the value is a list of rulesets
        """
        self.__registry.setdefault(cls, []).append(ruleset)

    def lookup(self, context=None):
        """ Return a component/adapter that implements Interface
            optionally, for a given context
            @context can be a tuple/list/dict in the case of multiadapters
        """

        """ Find candidates by interating through registry
            we end up with a dict of classes and their highest rating
        """
        candidates = {cls:
                      max([self._getspecificity(ruleset) for
                           ruleset in rulesets if ruleset(context)])
                      for cls, rulesets in self.__registry}

        """ Filter to get the top scoring candidates """
        candidates = sorted(candidates, key=key, reverse=True)
        maxscore = max(candidates.values())
        candidates = [candidate for candidate, score in candidates if
                      score == maxscore]

        """ If candidate implements an Interface that is derived
            from the requested one, take its specificity(depth) into
            account - NOT IMPLEMENTED. Is this needed?
            Do we want to track derived interfaces?
        """

        try:
            return candidates[0]
        except IndexError:
            raise CouldNotAdaptError("Could not find a suitable component for \
                                      interface %s" % self)

    """ Subscription """

    def subscribe(self, cls):
        pass

    def unsubscribe(self, cls):
        pass

    def issubscribed(self, cls):
        pass

    def getsubscribers(self, context=None):
        """ Return a generator of subscribers """
        pass

""" Create an instance which all interfaces extend """
Interface = InterfaceClass('Interface')

""" e.g
class MyInterfaceA(Interface):
    pass

class MyInterfaceB(Interface):
    pass

"""
