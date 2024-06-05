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
    '.eslintrc.cjs',
  ],
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
    eqeqeq: 'error',
    'require-await': 'error',
    'import/no-named-as-default': 'error',
    'import/no-default-export': 'error',
    '@typescript-eslint/await-thenable': 'error',
    'react/prop-types': 'error',
    '@typescript-eslint/prefer-string-starts-ends-with': 'error',
    '@typescript-eslint/ban-types': 'error',
    '@typescript-eslint/switch-exhaustiveness-check': 'error',
    '@typescript-eslint/no-unnecessary-type-arguments': 'error',
    '@typescript-eslint/no-unnecessary-boolean-literal-compare': 'error',
    '@typescript-eslint/no-floating-promises': 'error',
    '@typescript-eslint/no-unnecessary-condition': 'error',
    'react/self-closing-comp': ['error', { component: true, html: true }],

    'react-hooks/exhaustive-deps': 'warn', // TODO turn into error
  },
  overrides: [
    {
      files: ['*.stories.tsx'],
      rules: {
        'import/no-default-export': 'off',
      },
    },
    {
      files: ['cypress/**/*.ts'],
      parserOptions: {
        project: ['cypress/tsconfig.json'],
        tsconfigRootDir: __dirname,
        sourceType: 'module',
        ecmaVersion: 6,
      },
    },
  ],
}
