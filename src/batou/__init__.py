# This code must not cause non-stdlib imports to support self-bootstrapping.
from ._output import output


class UpdateNeeded(Exception):
    """A component requires an update."""


class ConfigurationError(Exception):
    """Indicates that an environment could not be configured successfully."""

    def __init__(self, message):
        self.message = message

    def report(self):
        output.error(self.message)


class ConversionError(ConfigurationError):
    """An override attribute could not be converted properly."""

    def __init__(self, component, key, value, conversion, error):
        self.component = component
        self.key = key
        self.value = value
        self.conversion = conversion
        self.error = error

    def report(self):
        output.error('Failed override attribute conversion')
        output.tabular(
            'Host', self.component.host.name,
            red=True)
        output.tabular(
            'Attribute',
            '{}.{}'.format(
                self.component._breadcrumbs,
                self.key),
            red=True)
        output.tabular('Conversion',
                       '{}({})'.format(self.conversion.__name__,
                                       repr(self.value)),
                       red=True)
        # TODO provide traceback in debug output
        output.tabular('Error', str(self.error), red=True)


class SilentConfigurationError(Exception):
    """These are exceptions that will be reported by other exceptions.

    They basically only influence control flow during configuration and
    are manually placed to avoid double reporting.

    """


class MissingOverrideAttributes(ConfigurationError):

    def __init__(self, component, attributes):
        self.component = component
        self.attributes = attributes

    def report(self):
        output.error('Overrides for undefined attributes')
        output.tabular(
            'Host', self.component.host.name,
            red=True)
        output.tabular(
            'Component',
            self.component._breadcrumbs,
            red=True)
        output.tabular(
            'Attributes',
            '.'.join(self.attributes),
            red=True)

        # TODO point to specific line in secrets or environments
        # cfg file and show context


class MissingComponent(ConfigurationError):

    def __init__(self, root):
        self.root = root

    def report(self):
        output.error('Missing component')
        output.tabular(
            'Host',
            self.component.host.name,
            red=True)
        output.tabular(
            'Component',
            self.root.name,
            red=True)


class DuplicateComponent(ConfigurationError):

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def report(self):
        output.error('Duplicate component "{}"'.format(self.a.__name_))
        output.tabular('Occurence', self.a.__file__)
        output.tabular('Occurence', self.b.__file__)


class UnknownComponentConfigurationError(ConfigurationError):
    """An unknown error occured while configuring a component."""

    def __init__(self, root, exception):
        self.root = root
        self.exception = exception

    def report(self):
        output.error("Unknown configuration error")
        output.annotate(
            "(Note, this might be batou bug, please report it.)", red=True)
        output.tabular(
            "Host", self.root.host.name, red=True)
        output.tabular(
            "Component", self.root.name, red=True)
        # TODO provide traceback in debug output
        output.tabular(
            "Exception", str(self.exception), red=True)


class UnusedResources(ConfigurationError):
    """Some provided resources were never used."""

    def __init__(self, resources):
        self.resources = resources

    def report(self):
        output.error("Unused provided resources")
        for key in self.resources:
            values = []
            for v in self.resources[key].values():
                values.extend(v)
            output.tabular(key, repr(values), red=True)


class UnsatisfiedResources(ConfigurationError):
    """Some required resources were never provided."""

    def __init__(self, resources):
        self.resources = resources

    def report(self):
        output.error("Unsatisfied resource requirements")
        for key in sorted(self.resources):
            output.tabular(key, '<undefined>', red=True)


class MissingEnvironment(ConfigurationError):
    """The specified environment does not exist."""

    def __init__(self, environment):
        self.environment = environment

    def report(self):
        output.error("Missing environment")
        output.tabular('Environment', self.environment.name, red=True)


class ComponentLoadingError(ConfigurationError):
    """The specified component file failed to load."""

    def __init__(self, filename, exception):
        self.filename = filename
        self.exception = exception

    def report(self):
        output.error("Failed loading component file")
        output.tabular("File", self.filename, red=True)
        output.tabular("Exception", str(self.exception), red=True)
        # TODO provide traceback in debug output


class SuperfluousSection(ConfigurationError):
    """A superfluous section was found in the environment
    configuration file."""

    def __init__(self, section):
        self.section = section

    def report(self):
        output.error("Superfluous section in environment configuration")
        output.tabular("Section", self.section, red=True)
        # TODO provide location and context in debug output


class SuperfluousComponentSection(ConfigurationError):
    """A component section was found in the environment
    but no associated component is known."""

    def __init__(self, component):
        self.component = component

    def report(self):
        output.error("Override section for unknown component found")
        output.tabular("Component", self.component, red=True)
        # TODO provide traceback in debug output


class SuperfluousSecretsSection(ConfigurationError):
    """A component section was found in the secrets
    but no associated component is known."""

    def __init__(self, component):
        self.component = component

    def report(self):
        output.error("Secrets section for unknown component found")
        output.tabular("Component", self.component, red=True)
        # TODO provide traceback in debug output


class CycleErrorDetected(ConfigurationError):
    """We think we found a cycle in the component dependencies.
    """

    def __init__(self, error):
        self.error = error

    def report(self):
        output.error("Found dependency cycle")
        output.annotate(str(self.error), red=True)
        # TODO provide traceback in debug output


class NonConvergingWorkingSet(ConfigurationError):
    """A working set did not converge."""

    def __init__(self, roots):
        self.roots = roots

    def report(self):
        # TODO show this last or first, but not in the middle
        # of everything
        output.error("{} remaining unconfigured components".format(
                     len(self.roots)))
        # TODO show all incl. their host name in -vv or so
        # output.annotate(', '.join(c.name for c in self.roots))


class DeploymentError(Exception):
    """Indicates that a deployment failed.."""
