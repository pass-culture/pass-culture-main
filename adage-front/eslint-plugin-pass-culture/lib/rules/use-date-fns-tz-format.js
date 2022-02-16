const isFormatInImports = listOfSpecifiers => {
  const foundFormat = listOfSpecifiers.find(
    specifier => specifier.imported?.name === 'format'
  )
  return !!foundFormat
}

const isDefaultImport = listOfSpecifiers => {
  const foundDefaultSpecifier = listOfSpecifiers.find(
    specifier => specifier.type === 'ImportDefaultSpecifier'
  )
  return !!foundDefaultSpecifier
}

const isImportAll = listOfSpecifiers => {
  const foundAllSpecifier = listOfSpecifiers.find(
    specifier => specifier.type === 'ImportNamespaceSpecifier'
  )
  return !!foundAllSpecifier
}

const isTimezoneInFormat = node => {
  const argumentsList = node.expression?.arguments
  const optionsArgument = argumentsList?.find(
    arg => arg.type === 'ObjectExpression'
  )
  const foundTimezoneInOptions = optionsArgument?.properties.find(
    property => property.key.name === 'timeZone'
  )
  return !!foundTimezoneInOptions
}

module.exports = {
  meta: {
    docs: {
      description:
        "Force the developer to use the format function from 'date-fns-tz' library instead of the one from 'date-fns' library, in order to think about timezone management",
    },
    messages: {
      useDateFnsTzFormat:
        'Please use the format function from date-fns-tz library instead of the one from date-fns. Please consider timezone of venue in datetime formatting.',
      importIndividualFunctions:
        'Please import individual function from date-fns library. If format function is needed, please import it from date-fns-tz and take timezone into account.',
      useTimezoneOption:
        'Please use timezone option in format arguments. As offers dates are sent as UTC from the backend, you need to take TZ into account.',
    },
  },
  create: context => ({
    ImportDeclaration: node => {
      if (
        (node.source.value === 'date-fns' &&
          isFormatInImports(node.specifiers)) ||
        (node.source.value === 'date-fns/format' &&
          isDefaultImport(node.specifiers))
      ) {
        context.report({
          node,
          messageId: 'useDateFnsTzFormat',
        })
      } else if (
        node.source.value === 'date-fns' &&
        isImportAll(node.specifiers)
      ) {
        context.report({
          node,
          messageId: 'importIndividualFunctions',
        })
      }
    },
    ExpressionStatement: node => {
      if (
        node.expression?.callee?.name === 'format' &&
        !isTimezoneInFormat(node)
      ) {
        context.report({
          node,
          messageId: 'useTimezoneOption',
        })
      }
    },
  }),
}
