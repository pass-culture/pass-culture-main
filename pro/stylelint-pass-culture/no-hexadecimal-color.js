const stylelint = require('stylelint')

const ruleName = 'pass-culture/no-hexadecimal-color'
const messages = stylelint.utils.ruleMessages(ruleName, {
  expected: (wrongValue, expectedValue) =>
    `Utiliser "${expectedValue}" à la place de "${wrongValue}".`,
})

module.exports = (primaryOption, secondaryOption, context) => (root, result) => {
  const isValidOptions = stylelint.utils.validateOptions(
    result,
    ruleName,
    { primaryOption },
    {
      actual: secondaryOption,
      possible: {
        colors: value => typeof value === 'object',
      },
      optional: false,
    }
  )

  if (!isValidOptions) return null

  root.walkDecls(node => {
    const hasSassVariable = node.prop.match(/\$/)

    if (hasSassVariable !== null) return null

    const wrongValueRegExp = node.value.match(/(#[0-9a-z]{3,8})/)
    const isIncluded =
      wrongValueRegExp !== null && Object.keys(secondaryOption.colors).includes(wrongValueRegExp[1])

    if (!isIncluded) return null

    const wrongValue = wrongValueRegExp[1]
    const goodValue = secondaryOption.colors[wrongValue]

    if (context.fix) {
      node.value = node.value.replace(wrongValue, goodValue)
    } else {
      stylelint.utils.report({
        message: messages.expected(wrongValue, goodValue),
        node,
        result,
        ruleName,
        word: wrongValue,
      })
    }
  })
}

module.exports.ruleName = ruleName
module.exports.messages = messages
