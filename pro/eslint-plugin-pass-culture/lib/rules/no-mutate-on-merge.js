const isValidMergeUsage = node => {
  if (!node.arguments[0]) {
    // This case is a little bit weird but not a usage that causes regression
    return true
  }

  if (node.arguments[0].type !== 'ObjectExpression') {
    return false
  }

  if (node.arguments[0].type === 'ObjectExpression' && node.arguments[0].properties.length > 0) {
    return false
  }

  return true
}

module.exports = {
  meta: {
    messages: {
      noMutateOnMerge: 'Veuillez utiliser un objet vide en premier pour ne pas muter la donnée.',
    },
  },
  create: context => ({
    CallExpression: node => {
      if (node.callee.name === 'merge' && !isValidMergeUsage(node)) {
        context.report({
          data: {
            name: node.callee.name,
          },
          node,
          messageId: 'noMutateOnMerge',
        })
      }
    },
  }),
}
