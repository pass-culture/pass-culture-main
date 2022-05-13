module.exports = {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  env: {
    browser: true,
    es6: true,
    jest: true,
    node: true,
  },
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  ignorePatterns: ['src/api/v1/gen/*', 'src/api/v2/gen/*'],
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 6,
  },
  rules: {
    '@typescript-eslint/ban-ts-comment': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-empty-function': 'off',
    'sort-imports': 1,
  },
  overrides: [
    {
      files: ['*.ts', '*.tsx', 'testcafe/**/*'],
      rules: {
        'no-undef': 'off',
      },
    },
  ],
}
