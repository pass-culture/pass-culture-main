/* global testRule */
const { messages, ruleName } = require('../no-font-properties')

testRule({
  plugins: ['./stylelint-pass-culture'],
  ruleName,
  config: [],
  reject: [
    {
      code: 'font: 14px arial;',
      message: messages.expected('font'),
    },
    {
      code: 'font-size: 14px;',
      message: messages.expected('font-size'),
    },
    {
      code: 'font-style: italic',
      message: messages.expected('font-style'),
    },
    {
      code: 'font-weight: 900;',
      message: messages.expected('font-weight'),
    },
  ],
})
