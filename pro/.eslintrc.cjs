module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:prettier/recommended',
    'plugin:import/recommended',
  ],
  env: {
    browser: true,
    es6: true,
    jest: true,
    node: true,
  },
  ignorePatterns: [
    'src/api/v1/gen/*',
    'src/api/v2/gen/*',
    '**/*.svg',
    '**/*.scss',
    '**/*.md',
    '**/*.jpg',
    '**/*.png',
    'src/index.html',
  ],
  overrides: [
    {
      files: ['*.ts', '*.tsx'],
      parser: '@typescript-eslint/parser',
      parserOptions: {
        project: ['./tsconfig.json'],
        tsconfigRootDir: __dirname,
        sourceType: 'module',
        ecmaVersion: 6,
      },
      plugins: ['@typescript-eslint'],
      extends: [
        'plugin:import/recommended',
        'eslint:recommended',
        'plugin:prettier/recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:react/recommended',
        'plugin:react-hooks/recommended',
      ],
      rules: {
        'import/no-unresolved': 0,
        'import/named': 0,
        curly: ['error', 'all'],
        'no-console': 1,
        'import/order': [
          'warn',
          {
            groups: [
              'builtin',
              'external',
              'internal',
              'parent',
              'sibling',
              'index',
            ],
            'newlines-between': 'always',
            alphabetize: { order: 'asc', caseInsensitive: true },
          },
        ],
        '@typescript-eslint/ban-ts-comment': 'off',
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-empty-function': 'off',
        'react/react-in-jsx-scope': 'off',
        '@typescript-eslint/prefer-ts-expect-error': 'error',
        'react/no-unescaped-entities': [
          'error',
          {
            forbid: [
              {
                char: "'",
                alternatives: ['’'],
              },
            ],
          },
        ],
        'require-await': 'error',
        'import/no-named-as-default': 'error',
        '@typescript-eslint/await-thenable': 'error',
        'react/prop-types': 'error',

        // TODO turn into errors
        '@typescript-eslint/no-floating-promises': 'warn',
        'react-hooks/exhaustive-deps': 'warn',
      },
    },
  ],
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      node: {
        extensions: ['.ts', '.tsx'],
        paths: ['.'],
        moduleDirectory: ['node_modules', 'src'],
      },
    },
  },
}
