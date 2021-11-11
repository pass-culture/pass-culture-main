/* global testRule */
const { messages, ruleName } = require('../no-hexadecimal-color')

testRule({
  plugins: ['./stylelint-pass-culture'],
  ruleName,
  config: [
    true,
    {
      colors: {
        '#0e2356': '$primary',
        '#8691aa': '$secondary',
        '#000000bb': '$black-shadow',
        '#000b': '$black-shadow-light',
      },
    },
  ],
  fix: true,
  accept: [
    {
      code: '$primary: #0e2356;',
    },
  ],
  reject: [
    {
      code: 'color: #0e2356;',
      fixed: 'color: $primary;',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'color: #000000bb;',
      fixed: 'color: $black-shadow;',
      message: messages.expected('#000000bb', '$black-shadow'),
    },
    {
      code: 'color: #000b;',
      fixed: 'color: $black-shadow-light;',
      message: messages.expected('#000b', '$black-shadow-light'),
    },
    {
      code: 'border: 1px solid #0e2356;',
      fixed: 'border: 1px solid $primary;',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'background: #0e2356 url() no-repeat;',
      fixed: 'background: $primary url() no-repeat;',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'background: #0e2356;',
      fixed: 'background: $primary;',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'background-color: #0e2356;',
      fixed: 'background-color: $primary;',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'box-shadow: 1px 1px 1px 1px rgba(#0e2356, .2);',
      fixed: 'box-shadow: 1px 1px 1px 1px rgba($primary, .2);',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'color: rgb(#0e2356, .2);',
      fixed: 'color: rgb($primary, .2);',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'color: hsl(#0e2356, .2);',
      fixed: 'color: hsl($primary, .2);',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'color: hsla(#0e2356, .2);',
      fixed: 'color: hsla($primary, .2);',
      message: messages.expected('#0e2356', '$primary'),
    },
    {
      code: 'color: #8691aa;',
      fixed: 'color: $secondary;',
      message: messages.expected('#8691aa', '$secondary'),
    },
  ],
})
