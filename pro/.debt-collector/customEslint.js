module.exports = {
  root: true,

  settings: {
    react: {
      version: 'detect',
    },
  },
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 'latest',
  },
  plugins: ['testing-library'],
  extends: ['plugin:testing-library/react'],
  rules: {
    complexity: ['error', 20],
    'max-depth': ['error', { max: 4 }],
    'max-lines': ['error', { max: 300, skipBlankLines: true }],
    'max-statements': ['error', 15],
    'max-lines-per-function': ['error', 50],
    'max-params': ['error', 5],
    'max-nested-callbacks': ['error', 5],
  },
}
