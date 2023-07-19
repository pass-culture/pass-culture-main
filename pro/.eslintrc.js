module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:prettier/recommended',
    'plugin:import/recommended',
  ],
  // This parser setting can be removed when there are no more JS files
  // here we use it to parse normal JS files
  parser: '@typescript-eslint/parser',
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 6,
  },
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
  ],
  // Rules for all files
  rules: {
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
  },
  overrides: [
    // Rules specific to TS files
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
      ],
      rules: {
        '@typescript-eslint/ban-ts-comment': 'off',
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-empty-function': 'off',
        '@typescript-eslint/prefer-ts-expect-error': 'error',
      },
    },
  ],
  settings: {
    react: {
      version: 'detect',
    },
    // This whole section can be removed when there are no more JS files
    'import/resolver': {
      node: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
        paths: ['.'],
        moduleDirectory: ['node_modules', 'src'],
      },
    },
  },
}
