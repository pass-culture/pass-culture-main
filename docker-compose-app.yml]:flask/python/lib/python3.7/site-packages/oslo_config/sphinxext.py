# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
import oslo_i18n
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx.domains import ObjType
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.nodes import make_refnode
from sphinx.util.nodes import nested_parse_with_titles

from oslo_config import cfg
from oslo_config import generator

LOG = logging.getLogger(__name__)


def _list_table(headers, data, title='', columns=None):
    """Build a list-table directive.

    :param add: Function to add one row to output.
    :param headers: List of header values.
    :param data: Iterable of row data, yielding lists or tuples with rows.
    """
    yield '.. list-table:: %s' % title
    yield '   :header-rows: 1'
    if columns:
        yield '   :widths: %s' % (','.join(str(c) for c in columns))
    yield ''
    yield '   - * %s' % headers[0]
    for h in headers[1:]:
        yield '     * %s' % h
    for row in data:
        yield '   - * %s' % row[0]
        for r in row[1:]:
            yield '     * %s' % r


def _indent(text, n=2):
    padding = ' ' * n
    # we don't want to indent blank lines so just output them as-is
    return '\n'.join(padding + x if x else '' for x in text.splitlines())


def _make_anchor_target(group_name, option_name):
    # We need to ensure this is unique across entire documentation
    # http://www.sphinx-doc.org/en/stable/markup/inline.html#ref-role
    target = '%s.%s' % (cfg._normalize_group_name(group_name),
                        option_name.lower())
    return target


_TYPE_DESCRIPTIONS = {
    cfg.StrOpt: 'string',
    cfg.BoolOpt: 'boolean',
    cfg.IntOpt: 'integer',
    cfg.FloatOpt: 'floating point',
    cfg.ListOpt: 'list',
    cfg.DictOpt: 'dict',
    cfg.MultiStrOpt: 'multi-valued',
    cfg.IPOpt: 'ip address',
    cfg.PortOpt: 'port number',
    cfg.HostnameOpt: 'hostname',
    cfg.URIOpt: 'URI',
    cfg.HostAddressOpt: 'host address',
    cfg._ConfigFileOpt: 'list of filenames',
    cfg._ConfigDirOpt: 'list of directory names',
}


def _get_choice_text(choice):
    if choice is None:
        return '<None>'
    elif choice == '':
        return "''"
    return str(choice)


def _format_opt(opt, group_name):
    opt_type = _TYPE_DESCRIPTIONS.get(type(opt),
                                      'unknown type')
    yield '.. oslo.config:option:: %s' % opt.dest
    yield ''
    yield _indent(':Type: %s' % opt_type)
    for default in generator._format_defaults(opt):
        if default:
            yield _indent(':Default: ``%s``' % default)
        else:
            yield _indent(':Default: ``%r``' % default)
    if getattr(opt.type, 'min', None) is not None:
        yield _indent(':Minimum Value: %s' % opt.type.min)
    if getattr(opt.type, 'max', None) is not None:
        yield _indent(':Maximum Value: %s' % opt.type.max)
    if getattr(opt.type, 'choices', None):
        choices_text = ', '.join([_get_choice_text(choice)
                                  for choice in opt.type.choices])
        yield _indent(':Valid Values: %s' % choices_text)
    try:
        if opt.mutable:
            yield _indent(
                ':Mutable: This option can be changed without restarting.'
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
        if not isinstance(cfg.Opt, opt):
            warnings.warn(
                'Incompatible option class for %s (%r): %s' %
                (opt.dest, opt.__class__, err),
            )
        else:
            warnings.warn('Failed to fully format sample for %s: %s' %
                          (opt.dest, err))
    if opt.advanced:
        yield _indent(
            ':Advanced Option: Intended for advanced users and not used')
        yield _indent(
            'by the majority of users, and might have a significant', 6)
        yield _indent(
            'effect on stability and/or performance.', 6)

    if opt.sample_default:
        yield _indent(
            '')
        yield _indent(
            'This option has a sample default set, which means that')
        yield _indent(
            'its actual default value may vary from the one documented')
        yield _indent(
            'above.')

    try:
        help_text = opt.help % {'default': 'the value above'}
    except (TypeError, KeyError, ValueError):
        # There is no mention of the default in the help string,
        # the string had some unknown key, or the string contained
        # invalid formatting characters
        help_text = opt.help
    if help_text:
        yield ''
        for line in help_text.strip().splitlines():
            yield _indent(line.rstrip())

    # We don't bother outputting this if not using new-style choices with
    # inline descriptions
    if getattr(opt.type, 'choices', None) and not all(
            x is None for x in opt.type.choices.values()):
        yield ''
        yield _indent('.. rubric:: Possible values')
        for choice in opt.type.choices:
            yield ''
            yield _indent(_get_choice_text(choice))
            yield _indent(_indent(
                opt.type.choices[choice] or '<No description provided>'))

    if opt.deprecated_opts:
        yield ''
        for line in _list_table(
                ['Group', 'Name'],
                ((d.group or group_name,
                  d.name or opt.dest or 'UNSET')
                 for d in opt.deprecated_opts),
                title='Deprecated Variations'):
            yield _indent(line)

    if opt.deprecated_for_removal:
        yield ''
        yield _indent('.. warning::')
        if opt.deprecated_since:
            yield _indent('   This option is deprecated for removal '
                          'since %s.' % opt.deprecated_since)
        else:
            yield _indent('   This option is deprecated for removal.')
        yield _indent('   Its value may be silently ignored ')
        yield _indent('   in the future.')
        if opt.deprecated_reason:
            reason = ' '.join([x.strip() for x in
                               opt.deprecated_reason.splitlines()])
            yield ''
            yield _indent('   :Reason: ' + reason)

    yield ''


def _format_group(namespace, group_name, group_obj):
    yield '.. oslo.config:group:: %s' % group_name
    if namespace:
        yield '   :namespace: %s' % namespace
    yield ''

    if group_obj and group_obj.help:
        for line in group_obj.help.strip().splitlines():
            yield _indent(line.rstrip())
        yield ''


def _format_group_opts(namespace, group_name, group_obj, opt_list):
    group_name = group_name or 'DEFAULT'
    LOG.debug('%s %s', namespace, group_name)

    for line in _format_group(namespace, group_name, group_obj):
        yield line

    for opt in opt_list:
        for line in _format_opt(opt, group_name):
            yield line


def _format_option_help(namespaces, split_namespaces):
    """Generate a series of lines of restructuredtext.

    Format the option help as restructuredtext and return it as a list
    of lines.
    """
    opts = generator._list_opts(namespaces)

    if split_namespaces:
        for namespace, opt_list in opts:
            for group, opts in opt_list:
                if isinstance(group, cfg.OptGroup):
                    group_name = group.name
                else:
                    group_name = group
                    group = None
                if group_name is None:
                    group_name = 'DEFAULT'
                lines = _format_group_opts(
                    namespace=namespace,
                    group_name=group_name,
                    group_obj=group,
                    opt_list=opts,
                )
                for line in lines:
                    yield line
    else:
        # Merge the options from different namespaces that belong to
        # the same group together and format them without the
        # namespace.
        by_section = {}
        group_objs = {}
        for ignore, opt_list in opts:
            for group, group_opts in opt_list:
                if isinstance(group, cfg.OptGroup):
                    group_name = group.name
                else:
                    group_name = group
                    group = None
                if group_name is None:
                    group_name = 'DEFAULT'
                group_objs.setdefault(group_name, group)
                by_section.setdefault(group_name, []).extend(group_opts)
        for group_name, group_opts in sorted(by_section.items()):
            lines = _format_group_opts(
                namespace=None,
                group_name=group_name,
                group_obj=group_objs.get(group_name),
                opt_list=group_opts,
            )
            for line in lines:
                yield line


class ShowOptionsDirective(rst.Directive):

    option_spec = {
        'split-namespaces': directives.flag,
        'config-file': directives.unchanged,
    }

    has_content = True

    def run(self):
        split_namespaces = 'split-namespaces' in self.options

        config_file = self.options.get('config-file')
        if config_file:
            LOG.info('loading config file %s', config_file)
            conf = cfg.ConfigOpts()
            conf.register_opts(generator._generator_opts)
            conf(
                args=['--config-file', config_file],
                project='oslo.config.sphinxext',
            )
            namespaces = conf.namespace[:]
        else:
            namespaces = [
                c.strip()
                for c in self.content
                if c.strip()
            ]

        result = ViewList()
        source_name = self.state.document.current_source

        for count, line in enumerate(_format_option_help(
                namespaces, split_namespaces)):
            result.append(line, source_name, count)
            LOG.debug('%5d%s%s', count, ' ' if line else '', line)

        node = nodes.section()
        node.document = self.state.document

        # With the resolution for bug #1755783, we now parse the 'Opt.help'
        # attribute as rST. Unfortunately, there are a lot of broken option
        # descriptions out there and we don't want to break peoples' builds
        # suddenly. As a result, we disable 'warning-is-error' temporarily.
        # Users will still see the warnings but the build will continue.
        with logging.skip_warningiserror():
            nested_parse_with_titles(self.state, result, node)

        return node.children


class ConfigGroupXRefRole(XRefRole):
    "Handles :oslo.config:group: roles pointing to configuration groups."

    def __init__(self):
        super(ConfigGroupXRefRole, self).__init__(
            warn_dangling=True,
        )

    def process_link(self, env, refnode, has_explicit_title, title, target):
        # The anchor for the group link is the group name.
        return target, target


class ConfigOptXRefRole(XRefRole):
    "Handles :oslo.config:option: roles pointing to configuration options."

    def __init__(self):
        super(ConfigOptXRefRole, self).__init__(
            warn_dangling=True,
        )

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            title = target
        if '.' in target:
            group, opt_name = target.split('.')
        else:
            group = 'DEFAULT'
            opt_name = target
        anchor = _make_anchor_target(group, opt_name)
        return title, anchor


class ConfigGroup(rst.Directive):

    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {
        'namespace': directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env

        group_name = self.arguments[0]
        namespace = self.options.get('namespace')

        cached_groups = env.domaindata['oslo.config']['groups']

        # Store the current group for use later in option directives
        env.temp_data['oslo.config:group'] = group_name
        LOG.debug('oslo.config group %s' % group_name)

        # Store the location where this group is being defined
        # for use when resolving cross-references later.
        # FIXME: This should take the source namespace into account, too
        cached_groups[group_name] = env.docname

        result = ViewList()
        source_name = '<' + __name__ + '>'

        def _add(text):
            "Append some text to the output result view to be parsed."
            result.append(text, source_name)

        if namespace:
            title = '%s: %s' % (namespace, group_name)
        else:
            title = group_name

        _add(title)
        _add('-' * len(title))
        _add('')
        for line in self.content:
            _add(line)
        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)

        first_child = node.children[0]

        # Compute the normalized target and set the node to have that
        # as an id
        target_name = cfg._normalize_group_name(group_name)
        first_child['ids'].append(target_name)

        indexnode = addnodes.index(entries=[])
        return [indexnode] + node.children


class ConfigOption(ObjectDescription):
    "Description of a configuration option (.. option)."

    def handle_signature(self, sig, signode):
        """Transform an option description into RST nodes."""
        optname = sig
        LOG.debug('oslo.config option %s', optname)
        # Insert a node into the output showing the option name
        signode += addnodes.desc_name(optname, optname)
        signode['allnames'] = [optname]
        return optname

    def add_target_and_index(self, firstname, sig, signode):
        cached_options = self.env.domaindata['oslo.config']['options']
        # Look up the current group name from the processing context
        currgroup = self.env.temp_data.get('oslo.config:group')
        # Compute the normalized target name for the option and give
        # that to the node as an id
        target_name = _make_anchor_target(currgroup, sig)
        signode['ids'].append(target_name)
        self.state.document.note_explicit_target(signode)
        # Store the location of the option definition for later use in
        # resolving cross-references
        # FIXME: This should take the source namespace into account, too
        cached_options[target_name] = self.env.docname


class ConfigDomain(Domain):
    """oslo.config domain."""
    name = 'oslo.config'
    label = 'oslo.config'
    object_types = {
        'configoption': ObjType('configuration option', 'option'),
    }
    directives = {
        'group': ConfigGroup,
        'option': ConfigOption,
    }
    roles = {
        'option': ConfigOptXRefRole(),
        'group': ConfigGroupXRefRole(),
    }
    initial_data = {
        'options': {},
        'groups': {},
    }

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        """Resolve cross-references"""
        if typ == 'option':
            group_name, option_name = target.split('.', 1)
            return make_refnode(
                builder,
                fromdocname,
                env.domaindata['oslo.config']['options'][target],
                target,
                contnode,
                option_name,
            )
        if typ == 'group':
            return make_refnode(
                builder,
                fromdocname,
                env.domaindata['oslo.config']['groups'][target],
                target,
                contnode,
                target,
            )
        return None


def setup(app):
    # NOTE(dhellmann): Try to turn off lazy translation from oslo_i18n
    # so any translated help text or deprecation messages associated
    # with configuration options are treated as regular strings
    # instead of Message objects. Unfortunately this is a bit
    # order-dependent, and so it's still possible that importing code
    # from another module such as through the autodoc features, or
    # even through the plugin scanner, will turn lazy evaluation back
    # on.
    oslo_i18n.enable_lazy(False)
    app.add_directive('show-options', ShowOptionsDirective)
    app.add_domain(ConfigDomain)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
