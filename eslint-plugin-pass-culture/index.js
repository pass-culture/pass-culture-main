module.exports = {
  rules: {
    'no-mutate-on-merge': require('./lib/rules/no-mutate-on-merge'),
  },
  configs: {
    recommended: {
      plugins: ['pass-culture'],
      rules: {
        'pass-culture/no-mutate-on-merge': 'error',
      },
    },
  },
}
