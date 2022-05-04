module.exports = {
  env: {
    browser: true,
    es6: true,
    jest: true,
    node: true,
  },
  parser: '@typescript-eslint/parser',
  ignorePatterns: ['src/api/v1/gen/*', 'src/api/v2/gen/*', '**/*.scss'],
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 6,
  },
}
