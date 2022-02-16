const RuleTester = require('eslint').RuleTester
const rule = require('eslint-plugin-pass-culture/lib/rules/use-date-fns-tz-format')

const parserOptions = require('./parserOptions')

const ruleTester = new RuleTester()

ruleTester.run('use-date-fns-tz', rule, {
  valid: [
    {
      code: '"ne pas utiliser date-fns"',
      parserOptions,
    },
    {
      code: "import isEqual from 'lodash.isequal'",
      parserOptions,
    },
    {
      code: "import { endOfDay } from 'date-fns'",
      parserOptions,
    },
    {
      code: "import * as date from 'date-fns-tz'",
      parserOptions,
    },
    {
      code: "format(date, dateFormat, { timeZone: 'UTC' })",
      parserOptions,
    },
  ],
  invalid: [
    {
      code: "import { format } from 'date-fns'",
      errors: [
        {
          messageId: 'useDateFnsTzFormat',
        },
      ],
      parserOptions,
    },
    {
      code: "import { endOfDay, format } from 'date-fns'",
      errors: [
        {
          messageId: 'useDateFnsTzFormat',
        },
      ],
      parserOptions,
    },
    {
      code: "import * as date from 'date-fns'",
      errors: [
        {
          messageId: 'importIndividualFunctions',
        },
      ],
      parserOptions,
    },
    {
      code: "import format from 'date-fns/format'",
      errors: [
        {
          messageId: 'useDateFnsTzFormat',
        },
      ],
      parserOptions,
    },
    {
      code: 'format(date, dateFormat)',
      errors: [
        {
          messageId: 'useTimezoneOption',
        },
      ],
      parserOptions,
    },
    {
      code: 'format(date, dateFormat, { locale: enGB })',
      errors: [
        {
          messageId: 'useTimezoneOption',
        },
      ],
      parserOptions,
    },
  ],
})
