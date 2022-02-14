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

module.exports = {
  meta: {
    docs: {
      description:
        "Force the developer to use the format function from 'date-fns-tz' library instead of the one from 'date-fns' library, in order to think about timezone management",
    },
    messages: {
      useDateFnsTzFormat:
        'Please use the format function from date-fns-tz library instead of the one from date-fns. Please consider timezone in datetime formatting.',
      importIndividualFunctions:
        'Please import individual function from date-fns library. If format function is needed, please import it from date-fns-tz and take timezone into account.',
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
  }),
}
