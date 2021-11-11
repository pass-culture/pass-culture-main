const RuleTester = require('eslint').RuleTester

const rule = require('../../../lib/rules/no-mutate-on-merge')

const parserOptions = require('./parserOptions')

const ruleTester = new RuleTester()

ruleTester.run('no-mutate-on-merge', rule, {
  valid: [
    {
      code: 'merge({}, initialData, overrideData)',
      parserOptions,
    },
    {
      code: 'merge()',
      parserOptions,
    },
    {
      code: 'otherFunction()',
      parserOptions,
    },
  ],
  invalid: [
    {
      code: 'merge(initialData, overrideData)',
      errors: [
        {
          messageId: 'noMutateOnMerge',
        },
      ],
      parserOptions,
    },
    {
      code: 'merge({ mutatedAttribute: "" }, initialData, overrideData)',
      errors: [
        {
          messageId: 'noMutateOnMerge',
        },
      ],
      parserOptions,
    },
  ],
})
