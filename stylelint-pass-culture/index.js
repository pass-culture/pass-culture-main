const createPlugin = require('stylelint').createPlugin

module.exports = [
  'no-hexadecimal-color',
].map((ruleName) => createPlugin(`pass-culture/${ruleName}`, require(`./${ruleName}`)))
