module.exports = {
  rules: {
    'use-date-fns-tz-format': require('eslint-plugin-pass-culture/lib/rules/use-date-fns-tz-format'),
  },
  configs: {
    recommended: {
      plugins: ['pass-culture'],
      rules: {
        'pass-culture/use-date-fns-tz-format': 'error',
      },
    },
  },
}
