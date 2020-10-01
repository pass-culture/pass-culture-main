# Copyright 2012 SINA Corporation
# Copyright 2014 Cisco Systems, Inc.
# All Rights Reserved.
# Copyright 2014 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Sample configuration generator

Tool for generating a sample configuration file. See
../doc/source/cli/generator.rst for details.

.. versionadded:: 1.4
"""

import collections
import copy
import json
import logging
import operator
import sys
import textwrap

try:
    # For Python 3.8 and later
    import importlib.metadata as importlib_metadata
except ImportError:
    # For everyone else
    import importlib_metadata

import yaml

from oslo_config import cfg
import stevedore.named  # noqa

LOG = logging.getLogger(__name__)
UPPER_CASE_GROUP_NAMES = ['DEFAULT']

_generator_opts = [
    cfg.StrOpt(
        'output-file',
        help='Path of the file to write to. Defaults to stdout.'),
    cfg.IntOpt(
        'wrap-width',
        default=70,
        help='The maximum length of help lines.'),
    cfg.MultiStrOpt(
        'namespace',
        required=True,
        help='Option namespace under "oslo.config.opts" in which to query '
        'for options.'),
    cfg.BoolOpt(
        'minimal',
        default=False,
        help='Generate a minimal required configuration.'),
    cfg.BoolOpt(
        'summarize',
        default=False,
        help='Only output summaries of help text to config files. Retain '
        'longer help text for Sphinx documents.'),
    cfg.StrOpt(
        'format',
        help='Desired format for the output.',
        default='ini',
        choices=[
            ('ini', 'The only format that can be used directly with '
             'oslo.config.'),
            ('json', 'Intended for third-party tools that want to write '
             'config files based on the sample config data.'),
            ('yaml', 'Same as json'),
            ('rst', 'Can be used to dump the text given to Sphinx when '
             'building documentation using the Sphinx extension. '
             'Useful for debugging,')
        ],
        dest='format_'),
]


def register_cli_opts(conf):
    """Register the formatter's CLI options with a ConfigOpts instance.

    Note, this must be done before the ConfigOpts instance is called to parse
    the configuration.

    :param conf: a ConfigOpts instance
    :raises: DuplicateOptError, ArgsAlreadyParsedError
    """
    conf.register_cli_opts(_generator_opts)


def _format_defaults(opt):
    "Return a list of formatted default values."
    if isinstance(opt, cfg.MultiStrOpt):
        if opt.sample_default is not None:
            defaults = opt.sample_default
        elif not opt.default:
            defaults = ['']
        else:
            defaults = opt.default
    else:
        if opt.sample_default is not None:
            default_str = str(opt.sample_default)
        elif opt.default is None:
            default_str = '<None>'
        elif isinstance(opt, (cfg.StrOpt, cfg.IntOpt, cfg.FloatOpt, cfg.IPOpt,
                              cfg.PortOpt, cfg.HostnameOpt, cfg.HostAddressOpt,
                              cfg.URIOpt, cfg.Opt)):
            default_str = str(opt.default)
        elif isinstance(opt, cfg.BoolOpt):
            default_str = str(opt.default).lower()
        elif isinstance(opt, (cfg.ListOpt, cfg._ConfigFileOpt,
                              cfg._ConfigDirOpt)):
            default_str = ','.join(str(d) for d in opt.default)
        elif isinstance(opt, cfg.DictOpt):
            sorted_items = sorted(opt.default.items(),
                                  key=operator.itemgetter(0))
            default_str = ','.join(['%s:%s' % i for i in sorted_items])
        else:
            LOG.warning('Unknown option type: %s', repr(opt))
            default_str = str(opt.default)
        defaults = [default_str]

    results = []
    for default_str in defaults:
        if not isinstance(default_str, str):
            default_str = str(default_str)
        if default_str.strip() != default_str:
            default_str = '"%s"' % default_str
        results.append(default_str)
    return results


_TYPE_NAMES = {
    str: 'string value',
    int: 'integer value',
    float: 'floating point value',
}


def _format_type_name(opt_type):
    """Format the type name to use in describing an option"""
    try:
        return opt_type.type_name
    except AttributeError:  # nosec
        pass

    try:
        return _TYPE_NAMES[opt_type]
    except KeyError:  # nosec
        pass

    return 'unknown value'


class _OptFormatter(object):

    """Format configuration option descriptions to a file."""

    def __init__(self, conf, output_file=None):
        """Construct an OptFormatter object.

        :param conf: The config object from _generator_opts
        :param output_file: a writeable file object
        """
        self.output_file = output_file or sys.stdout
        self.wrap_width = conf.wrap_width
        self.minimal = conf.minimal
        self.summarize = conf.summarize

    def _format_help(self, help_text):
        """Format the help for a group or option to the output file.

        :param help_text: The text of the help string
        """
        if self.wrap_width is not None and self.wrap_width > 0:
            wrapped = ""
            for line in help_text.splitlines():
                text = "\n".join(textwrap.wrap(line, self.wrap_width,
                                               initial_indent='# ',
                                               subsequent_indent='# ',
                                               break_long_words=False,
                                               replace_whitespace=False))
                wrapped += "#" if text == "" else text
                wrapped += "\n"
            lines = [wrapped]
        else:
            lines = ['# ' + help_text + '\n']
        return lines

    def _get_choice_text(self, choice):
        if choice is None:
            return '<None>'
        elif choice == '':
            return "''"
        return str(choice)

    def format_group(self, group_or_groupname):
        """Format the description of a group header to the output file

        :param group_or_groupname: a cfg.OptGroup instance or a name of group
        :returns: a formatted group description string
        """
        if isinstance(group_or_groupname, cfg.OptGroup):
            group = group_or_groupname
            lines = ['[%s]\n' % group.name]
            if group.help:
                lines += self._format_help(group.help)
        else:
            groupname = group_or_groupname
            lines = ['[%s]\n' % groupname]
        self.writelines(lines)

    def format(self, opt, group_name):
        """Format a description of an option to the output file.

        :param opt: a cfg.Opt instance
        :param group_name: name of the group to which the opt is assigned
        :returns: a formatted opt description string
        """
        if not opt.help:
            LOG.warning('"%s" is missing a help string', opt.dest)

        opt_type = _format_type_name(opt.type)
        opt_prefix = ''
        if (opt.deprecated_for_removal and
                not opt.help.startswith('DEPRECATED')):
            opt_prefix = 'DEPRECATED: '

        if opt.help:
            # an empty line signifies a new paragraph. We only want the
            # summary line
            if self.summarize:
                _split = opt.help.split('\n\n')
                opt_help = _split[0].rstrip(':').rstrip('.')
                if len(_split) > 1:
                    opt_help += '. For more information, refer to the '
                    opt_help += 'documentation.'
            else:
                opt_help = opt.help

            help_text = u'%s%s (%s)' % (opt_prefix,
                                        opt_help,
                                        opt_type)
        else:
            help_text = u'(%s)' % opt_type
        lines = self._format_help(help_text)

        if getattr(opt.type, 'min', None) is not None:
            lines.append('# Minimum value: {}\n'.format(opt.type.min))

        if getattr(opt.type, 'max', None) is not None:
            lines.append('# Maximum value: {}\n'.format(opt.type.max))

        if getattr(opt.type, 'choices', None):
            lines.append('# Possible values:\n')
            for choice in opt.type.choices:
                help_text = '%s - %s' % (
                    self._get_choice_text(choice),
                    opt.type.choices[choice] or '<No description provided>')
                lines.extend(self._format_help(help_text))

        try:
            if opt.mutable:
                lines.append(
                    '# Note: This option can be changed without restarting.\n'
                )
        except AttributeError as err:
            # NOTE(dhellmann): keystoneauth defines its own Opt class,
            # and neutron (at least) returns instances of those
            # classes instead of oslo_config Opt instances. The new
            # mutable attribute is the first property where the API
            # isn't supported in the external class, so we can use
            # this failure to emit a warning. See
            # https://bugs.launchpad.net/keystoneauth/+bug/1548433 for
            # more details.
            import warnings
            if not isinstance(opt, cfg.Opt):
                warnings.warn(
                    'Incompatible option class for %s (%r): %s' %
                    (opt.dest, opt.__class__, err),
                )
            else:
                warnings.warn('Failed to fully format sample for %s: %s' %
                              (opt.dest, err))

        for d in opt.deprecated_opts:
            # NOTE(bnemec): opt names with a - are not valid in a config file,
            # but it is possible to add a DeprecatedOpt with a - name.  We
            # want to ignore those as they won't work anyway.
            if d.name and '-' not in d.name:
                lines.append('# Deprecated group/name - [%s]/%s\n' %
                             (d.group or group_name, d.name or opt.dest))

        if opt.deprecated_for_removal:
            if opt.deprecated_since:
                lines.append(
                    '# This option is deprecated for removal since %s.\n' % (
                        opt.deprecated_since))
            else:
                lines.append(
                    '# This option is deprecated for removal.\n')
            lines.append(
                '# Its value may be silently ignored in the future.\n')
            if opt.deprecated_reason:
                lines.extend(
                    self._format_help('Reason: ' + opt.deprecated_reason))

        if opt.advanced:
            lines.append(
                '# Advanced Option: intended for advanced users and not used\n'
                '# by the majority of users, and might have a significant\n'
                '# effect on stability and/or performance.\n'
            )

        if opt.sample_default:
            lines.append(
                '#\n'
                '# This option has a sample default set, which means that\n'
                '# its actual default value may vary from the one documented\n'
                '# below.\n'
            )

        if hasattr(opt.type, 'format_defaults'):
            defaults = opt.type.format_defaults(opt.default,
                                                opt.sample_default)
        else:
            LOG.debug(
                "The type for option %(name)s which is %(type)s is not a "
                "subclass of types.ConfigType and doesn't provide a "
                "'format_defaults' method. A default formatter is not "
                "available so the best-effort formatter will be used.",
                {'type': opt.type, 'name': opt.name})
            defaults = _format_defaults(opt)
        for default_str in defaults:
            if default_str:
                default_str = ' ' + default_str.replace('\n', '\n#    ')
            if self.minimal:
                lines.append('%s =%s\n' % (opt.dest, default_str))
            else:
                lines.append('#%s =%s\n' % (opt.dest, default_str))

        self.writelines(lines)

    def write(self, s):
        """Write an arbitrary string to the output file.

        :param s: an arbitrary string
        """
        self.output_file.write(s)

    def writelines(self, lines):
        """Write an arbitrary sequence of strings to the output file.

        :param lines: a list of arbitrary strings
        """
        self.output_file.writelines(lines)


def _cleanup_opts(read_opts):
    """Cleanup duplicate options in namespace groups

    Return a structure which removes duplicate options from a namespace group.
    NOTE:(rbradfor) This does not remove duplicated options from repeating
    groups in different namespaces:

    :param read_opts: a list (namespace, [(group, [opt_1, opt_2])]) tuples
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """

    # OrderedDict is used specifically in the three levels to maintain the
    # source order of namespace/group/opt values
    clean = collections.OrderedDict()
    for namespace, listing in read_opts:
        if namespace not in clean:
            clean[namespace] = collections.OrderedDict()
        for group, opts in listing:
            # NOTE: Normalize group names to lowe-case except those defined in
            # UPPER_CASE_GROUP_NAMES
            if group:
                group_name = getattr(group, 'name', str(group))
                if group_name.upper() in UPPER_CASE_GROUP_NAMES:
                    normalized_gn = group_name.upper()
                else:
                    normalized_gn = group_name.lower()
                if normalized_gn != group_name:
                    LOG.warning('normalizing group name %r to %r', group_name,
                                normalized_gn)
                    if hasattr(group, 'name'):
                        group.name = normalized_gn
                    else:
                        group = normalized_gn

            if group not in clean[namespace]:
                clean[namespace][group] = collections.OrderedDict()
            for opt in opts:
                clean[namespace][group][opt.dest] = opt

    # recreate the list of (namespace, [(group, [opt_1, opt_2])]) tuples
    # from the cleaned structure.
    cleaned_opts = [
        (namespace, [(g, list(clean[namespace][g].values()))
                     for g in clean[namespace]])
        for namespace in clean
    ]

    return cleaned_opts


def _get_raw_opts_loaders(namespaces):
    """List the options available via the given namespaces.

    :param namespaces: a list of namespaces registered under 'oslo.config.opts'
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """
    mgr = stevedore.named.NamedExtensionManager(
        'oslo.config.opts',
        names=namespaces,
        on_load_failure_callback=on_load_failure_callback,
        invoke_on_load=False)
    return [(e.name, e.plugin) for e in mgr]


def _get_driver_opts_loaders(namespaces, driver_option_name):
    mgr = stevedore.named.NamedExtensionManager(
        namespace='oslo.config.opts.' + driver_option_name,
        names=namespaces,
        on_load_failure_callback=on_load_failure_callback,
        invoke_on_load=False)
    return [(e.name, e.plugin) for e in mgr]


def _get_driver_opts(driver_option_name, namespaces):
    """List the options available from plugins for drivers based on the option.

    :param driver_option_name: The name of the option controlling the
                               driver options.
    :param namespaces: a list of namespaces registered under
                       'oslo.config.opts.' + driver_option_name
    :returns: a dict mapping driver name to option list

    """
    all_opts = {}
    loaders = _get_driver_opts_loaders(namespaces, driver_option_name)
    for plugin_name, loader in loaders:
        for driver_name, option_list in loader().items():
            all_opts.setdefault(driver_name, []).extend(option_list)
    return all_opts


def _get_opt_default_updaters(namespaces):
    mgr = stevedore.named.NamedExtensionManager(
        'oslo.config.opts.defaults',
        names=namespaces,
        warn_on_missing_entrypoint=False,
        on_load_failure_callback=on_load_failure_callback,
        invoke_on_load=False)
    return [ep.plugin for ep in mgr]


def _update_defaults(namespaces):
    "Let application hooks update defaults inside libraries."
    for update in _get_opt_default_updaters(namespaces):
        update()


def _list_opts(namespaces):
    """List the options available via the given namespaces.

    Duplicate options from a namespace are removed.

    :param namespaces: a list of namespaces registered under 'oslo.config.opts'
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """
    # Load the functions to get the options.
    loaders = _get_raw_opts_loaders(namespaces)
    # Update defaults, which might change global settings in library
    # modules.
    _update_defaults(namespaces)
    # Ask for the option definitions. At this point any global default
    # changes made by the updaters should be in effect.
    response = []
    for namespace, loader in loaders:
        # The loaders return iterables for the group opts, and we need
        # to extend them, so build a list.
        namespace_values = []
        # Look through the groups and find any that need drivers so we
        # can load those extra options.
        for group, group_opts in loader():
            # group_opts is an iterable but we are going to extend it
            # so convert it to a list.
            group_opts = list(group_opts)
            if isinstance(group, cfg.OptGroup):
                if group.driver_option:
                    # Load the options for all of the known drivers.
                    driver_opts = _get_driver_opts(
                        group.driver_option,
                        namespaces,
                    )
                    # Save the list of names of options for each
                    # driver in the group for use later. Add the
                    # options to the group_opts list so they are
                    # processed along with the static options in that
                    # group.
                    driver_opt_names = {}
                    for driver_name, opts in sorted(driver_opts.items()):
                        # Multiple plugins may add values to the same
                        # driver name, so combine the lists we do
                        # find.
                        driver_opt_names.setdefault(driver_name, []).extend(
                            o.name for o in opts)
                        group_opts.extend(opts)
                    group._save_driver_opts(driver_opt_names)
            namespace_values.append((group, group_opts))
        response.append((namespace, namespace_values))
    return _cleanup_opts(response)


def on_load_failure_callback(*args, **kwargs):
    raise


def _output_opts(f, group, group_data):
    f.format_group(group_data['object'] or group)
    for (namespace, opts) in sorted(group_data['namespaces'],
                                    key=operator.itemgetter(0)):
        f.write('\n#\n# From %s\n#\n' % namespace)
        for opt in sorted(opts, key=operator.attrgetter('advanced')):
            try:
                if f.minimal and not opt.required:
                    pass
                else:
                    f.write('\n')
                    f.format(opt, group)
            except Exception as err:
                f.write('# Warning: Failed to format sample for %s\n' %
                        (opt.dest,))
                f.write('# %s\n' % (err,))


def _get_groups(conf_ns):
    """Invert a list of groups by namespace into a dict by group name.

    :param conf_ns: a list of (namespace, [(<group>, [opt_1, opt_2])]) tuples,
                    such as returned by _list_opts.
    :returns: {<group_name>, {'object': <group_object>,
                              'namespaces': [(<namespace>, <opts>)]}}

    <group> may be a string or a group object.
    <group_name> is always a string.
    <group_object> will only be set if <group> was a group object in at least
    one namespace.

    Keying by group_name avoids adding duplicate group names in case a group is
    added as both an OptGroup and as a str, but still makes the additional
    OptGroup data available to the output code when possible.
    """
    groups = {'DEFAULT': {'object': None, 'namespaces': []}}
    for namespace, listing in conf_ns:
        for group, opts in listing:
            if not opts:
                continue
            group = group if group else 'DEFAULT'
            is_optgroup = hasattr(group, 'name')
            group_name = group.name if is_optgroup else group
            if group_name not in groups:
                groups[group_name] = {'object': None, 'namespaces': []}
            if is_optgroup:
                groups[group_name]['object'] = group
            groups[group_name]['namespaces'].append((namespace, opts))
    return groups


def _build_entry(opt, group, namespace, conf):
    """Return a dict representing the passed in opt

    The dict will contain all public attributes of opt, as well as additional
    entries for namespace, choices, min, and max.  Any DeprecatedOpts
    contained in the deprecated_opts member will be converted to a dict with
    the format: {'group': <deprecated group>, 'name': <deprecated name>}

    :param opt: The Opt object to represent as a dict.
    :param group: The name of the group containing opt.
    :param namespace: The name of the namespace containing opt.
    :param conf: The ConfigOpts object containing the options for the
                 generator tool
    """
    entry = {key: value for key, value in opt.__dict__.items()
             if not key.startswith('_')}
    entry['namespace'] = namespace
    # Where present, we store choices as an OrderedDict. The default repr for
    # this is not very machine readable, thus, it is switched to a list of
    # tuples here. In addition, in some types, choices is explicitly set to
    # None. Force these cases to [] so it is always an iterable type.
    if getattr(entry['type'], 'choices', None):
        entry['choices'] = list(entry['type'].choices.items())
    else:
        entry['choices'] = []
    entry['min'] = getattr(entry['type'], 'min', None)
    entry['max'] = getattr(entry['type'], 'max', None)
    entry['type'] = _format_type_name(entry['type'])
    deprecated_opts = []
    for deprecated_opt in entry['deprecated_opts']:
        # NOTE(bnemec): opt names with a - are not valid in a config file,
        # but it is possible to add a DeprecatedOpt with a - name.  We
        # want to ignore those as they won't work anyway.
        if not deprecated_opt.name or '-' not in deprecated_opt.name:
            deprecated_opts.append(
                {'group': deprecated_opt.group or group,
                 'name': deprecated_opt.name or entry['name'],
                 })
    entry['deprecated_opts'] = deprecated_opts
    return entry


def _generate_machine_readable_data(groups, conf):
    """Create data structure for machine readable sample config

    Returns a dictionary with the top-level keys 'options',
    'deprecated_options', and 'generator_options'.

    'options' contains a dict mapping group names to a list of options in
    that group.  Each option is represented by the result of a call to
    _build_entry.  Only non-deprecated options are included in this list.

    'deprecated_options' contains a dict mapping groups names to a list of
    opts from that group which were deprecated.

    'generator_options' is a dict mapping the options for the sample config
    generator itself to their values.

    :param groups: A dict of groups as returned by _get_groups.
    :param conf: The ConfigOpts object containing the options for the
                 generator tool
    """
    output_data = {'options': {},
                   'deprecated_options': {},
                   'generator_options': {}}
    # See _get_groups for details on the structure of group_data
    for group_name, group_data in groups.items():
        output_group = {'opts': [], 'help': ''}
        output_data['options'][group_name] = output_group
        for namespace in group_data['namespaces']:
            for opt in namespace[1]:
                if group_data['object']:
                    output_group.update(
                        group_data['object']._get_generator_data()
                    )
                else:
                    output_group.update({
                        'dynamic_group_owner': '',
                        'driver_option': '',
                        'driver_opts': {},
                    })
                entry = _build_entry(opt, group_name, namespace[0], conf)
                output_group['opts'].append(entry)
                # Need copies of the opts because we modify them
                for deprecated_opt in copy.deepcopy(entry['deprecated_opts']):
                    group = deprecated_opt.pop('group')
                    deprecated_options = output_data['deprecated_options']
                    deprecated_options.setdefault(group, [])
                    deprecated_opt['replacement_name'] = entry['name']
                    deprecated_opt['replacement_group'] = group_name
                    deprecated_options[group].append(deprecated_opt)
        # Build the list of options in the group that are not tied to
        # a driver.
        non_driver_opt_names = [
            o['name']
            for o in output_group['opts']
            if not any(o['name'] in output_group['driver_opts'][d]
                       for d in output_group['driver_opts'])
        ]
        output_group['standard_opts'] = non_driver_opt_names

    output_data['generator_options'] = dict(conf)
    return output_data


def _output_machine_readable(groups, output_file, conf):
    """Write a machine readable sample config file

    Take the data returned by _generate_machine_readable_data and write it in
    the format specified by the format_ attribute of conf.

    :param groups: A dict of groups as returned by _get_groups.
    :param output_file: A file-like object to which the data should be written.
    :param conf: The ConfigOpts object containing the options for the
                 generator tool
    """
    output_data = _generate_machine_readable_data(groups, conf)
    if conf.format_ == 'yaml':
        output_file.write(yaml.safe_dump(output_data,
                                         default_flow_style=False))
    else:
        output_file.write(json.dumps(output_data, sort_keys=True))
    output_file.write('\n')


def _output_human_readable(namespaces, output_file):
    """Write an RST formated version of the docs for the options.

    :param groups: A list of the namespaces to use for discovery.
    :param output_file: A file-like object to which the data should be written.
    """
    try:
        from oslo_config import sphinxext
    except ImportError:
        raise RuntimeError(
            'Could not import sphinxext. '
            'Please install Sphinx and try again.',
        )
    output_data = list(sphinxext._format_option_help(
        LOG, namespaces, False))
    output_file.write('\n'.join(output_data))


def generate(conf, output_file=None):
    """Generate a sample config file.

    List all of the options available via the namespaces specified in the given
    configuration and write a description of them to the specified output file.

    :param conf: a ConfigOpts instance containing the generator's configuration
    """
    conf.register_opts(_generator_opts)

    own_file = False

    if output_file is None:
        if conf.output_file:
            output_file = open(conf.output_file, 'w')
            own_file = True
        else:
            output_file = sys.stdout

    groups = _get_groups(_list_opts(conf.namespace))

    if conf.format_ == 'ini':
        formatter = _OptFormatter(conf, output_file=output_file)

        # Output the "DEFAULT" section as the very first section
        _output_opts(formatter, 'DEFAULT', groups.pop('DEFAULT'))

        # output all other config sections with groups in alphabetical order
        for group, group_data in sorted(groups.items()):
            formatter.write('\n\n')
            _output_opts(formatter, group, group_data)
    elif conf.format_ == 'rst':
        _output_human_readable(
            conf.namespace,
            output_file=output_file,
        )
    else:
        _output_machine_readable(groups,
                                 output_file=output_file,
                                 conf=conf)

    if own_file:
        output_file.close()


def main(args=None):
    """The main function of oslo-config-generator."""
    version = importlib_metadata.version('oslo.config')
    logging.basicConfig(level=logging.WARN)
    conf = cfg.ConfigOpts()
    register_cli_opts(conf)
    try:
        conf(args, version=version)
    except cfg.RequiredOptError:
        conf.print_help()
        if not sys.argv[1:]:
            raise SystemExit
        raise
    generate(conf)


if __name__ == '__main__':
    main()
