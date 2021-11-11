const createPlugin = require('stylelint').createPlugin

module.exports = ['no-font-properties', 'no-hexadecimal-color'].map(ruleName =>
  createPlugin(`pass-culture/${ruleName}`, require(`./${ruleName}`))
)
