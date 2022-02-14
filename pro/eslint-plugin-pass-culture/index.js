module.exports = {
  rules: {
    'no-mutate-on-merge': require('./lib/rules/no-mutate-on-merge'),
    'use-date-fns-tz-format': require('./lib/rules/use-date-fns-tz-format'),
  },
  configs: {
    recommended: {
      plugins: ['pass-culture'],
      rules: {
        'pass-culture/no-mutate-on-merge': 'error',
        'pass-culture/use-date-fns-tz-format': 'error',
      },
    },
  },
}
