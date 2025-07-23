import { fixupPluginRules } from '@eslint/compat'
import eslint from '@eslint/js'

import cypressPlugin from 'eslint-plugin-cypress/flat'
import importPlugin from 'eslint-plugin-import'
import reactPlugin from 'eslint-plugin-react'
import reactHooksPlugin from 'eslint-plugin-react-hooks'

import tseslint from 'typescript-eslint'

import globals from 'globals'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default tseslint.config(
  // register all of the plugins up-front
  {
    plugins: {
      ['@typescript-eslint']: tseslint.plugin,
      ['cypress']: cypressPlugin,
      ['import']: importPlugin,
      ['react']: reactPlugin,
      ['react-hooks']: fixupPluginRules(reactHooksPlugin),
    },
  },
  // config with just ignores is the replacement for `.eslintignore`
  {
    ignores: [
      'src/apiClient/*',
      'src/api/v1/gen/*',
      'src/api/v2/gen/*',
      'scripts/*',
      '**/*.svg',
      '**/*.scss',
      '**/*.md',
      '**/*.mdx',
      '**/*.jpg',
      '**/*.png',
      'src/index.html',
      '**/eslint.config.mjs',
      '**/cypress.config.ts',
      '**/vite.config.ts',
      '.storybook/*',
      'src/**/*.gif',
    ],
  },
  // extends ...
  eslint.configs.recommended,
  tseslint.configs.recommended,
  cypressPlugin.configs.recommended,
  reactPlugin.configs.flat.recommended,
  reactPlugin.configs.flat['jsx-runtime'],
  // base config
  {
    files: ['**/*.tsx', '**/*.ts'],
    linterOptions: { reportUnusedDisableDirectives: false },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.jest,
        ...globals.node,
        React: true,
        JSX: true,
        vi: true,
      },
      parserOptions: {
        project: ['./tsconfig.json', './cypress/tsconfig.json'],
        tsconfigRootDir: __dirname,
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    rules: {
      // OFF rules, fix them later or comment why they are off
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/no-empty-function': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-expressions': 'off',
      'prefer-const': 'off',
      'prefer-rest-params': 'off',
      'react/react-in-jsx-scope': 'off',
      // import/* rules turned OFF because of Typescript compiler, following
      // https://typescript-eslint.io/troubleshooting/typed-linting/performance/#eslint-plugin-import recommendations.
      'import/named': 'off',
      'import/namespace': 'off',
      'import/default': 'off',
      'import/no-named-as-default': 'off',
      'import/no-unresolved': 'off',

      // extra ERROR rules, evntually duplicate with recommended
      '@typescript-eslint/await-thenable': 'error',
      '@typescript-eslint/prefer-string-starts-ends-with': 'error',
      '@typescript-eslint/naming-convention': [
        'error',
        {
          selector: 'typeAlias',
          format: ['PascalCase'],
        },
      ],
      '@typescript-eslint/no-restricted-types': 'error',
      '@typescript-eslint/no-empty-object-type': 'error',
      '@typescript-eslint/no-unsafe-function-type': 'error',
      '@typescript-eslint/no-wrapper-object-types': 'error',
      '@typescript-eslint/no-unnecessary-type-arguments': 'error',
      '@typescript-eslint/no-unnecessary-boolean-literal-compare': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-unnecessary-condition': 'error',
      '@typescript-eslint/prefer-ts-expect-error': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      eqeqeq: 'error',
      curly: ['error', 'all'],
      'import/export': 'error',
      'import/no-default-export': 'error',
      'no-console': 'error',
      'require-await': 'error',
      'react/forbid-elements': [
        2,
        {
          forbid: [
            {
              element: 'DevTool',
              message: "Don't forget to remove before commit",
            },
            {
              element: 'MainHeading',
              message:
                'Avoid the use of `<MainHeading>` inside a component. Rather use the `<Layout>` component with the `mainHeading` prop whenever possible',
            },
          ],
        },
      ],
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
      'react/prop-types': 'error',
      'react-hooks/rules-of-hooks': 'error',

      // extra WARNING rules, evntually duplicate with recommended
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
          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },
        },
      ],
      'import/no-duplicates': 'warn',
      'import/no-dynamic-require': 'warn',
      'import/no-named-as-default-member': 'warn',
      'import/no-nodejs-modules': 'warn',
      'react-hooks/exhaustive-deps': 'warn',
    },
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
  },
  {
    files: ['cypress/**/*.ts'],
    languageOptions: {
      ecmaVersion: 6,
      sourceType: 'module',
    },
  },
  {
    files: ['**/*.stories.tsx'],
    rules: {
      'import/no-default-export': 'off',
    },
  }
)
