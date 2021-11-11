const stylelint = require('stylelint')

const ruleName = 'pass-culture/no-font-properties'
const messages = stylelint.utils.ruleMessages(ruleName, {
  expected: wrongValue =>
    `Ne pas utiliser "${wrongValue}" mais plutôt la mixin associée avec "@include MaMixin();".`,
})

module.exports = () => (root, result) => {
  root.walkDecls(node => {
    const wrongValueRegExp = ['font', 'font-size', 'font-style', 'font-weight']
    const isIncluded = wrongValueRegExp.includes(node.prop)

    if (!isIncluded) return null

    const wrongValue = node.prop

    stylelint.utils.report({
      message: messages.expected(wrongValue),
      node,
      result,
      ruleName,
      word: wrongValue,
    })
  })
}

module.exports.ruleName = ruleName
module.exports.messages = messages
