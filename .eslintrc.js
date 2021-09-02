const newStrictConfig = process.env.ESLINT === 'NEW_CONFIG'

const comonConfig = {
  extends: [
    'eslint:recommended',
    'plugin:react/all',
    'plugin:jsx-a11y/strict',
    'plugin:import/errors',
    'plugin:jest/all',
    'plugin:pass-culture/recommended',
    'plugin:react-hooks/recommended',
  ],
  env: {
    browser: true,
    es6: true,
    jest: true,
    node: true,
  },
  globals: {
    fixture: 'readonly',
  },
  parser: '@typescript-eslint/parser',
  plugins: ['only-warn'],
  rules: {
    indent: [
      'warn',
      2,
      { ignoredNodes: ['JSXElement'], offsetTernaryExpressions: true, SwitchCase: 1 },
    ],
    'import/order': [
      'warn',
      {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
        'newlines-between': 'always',
        alphabetize: { order: 'asc', caseInsensitive: true },
      },
    ],
    'object-curly-spacing': ['error', 'always'],
    'jest/no-hooks': 'off',
    'jest/prefer-expect-assertions': 'off',
    'jest/prefer-inline-snapshots': 'off',
    'jsx-a11y/label-has-for': 'off',
    'jsx-a11y/no-onchange': 'off',
    'no-var': 'warn',
    'react/forbid-component-props': 'off',
    'react/function-component-definition': [
      2,
      {
        namedComponents: 'arrow-function',
        unnamedComponents: 'arrow-function',
      },
    ],
    'react/jsx-no-literals': 'off',
    'react/jsx-curly-brace-presence': [2, { props: 'never', children: 'never' }],
    'react/jsx-filename-extension': [1, { extensions: ['.jsx', '.tsx'] }],
    'react/jsx-fragments': 'off',
    'react/jsx-indent': [2, 2, { indentLogicalExpressions: true }],
    'react/jsx-indent-props': [2, 2],
    'react/jsx-handler-names': 'off',
    'react/jsx-max-depth': 'off',
    'react/jsx-newline': 'off',
    'react/jsx-props-no-spreading': 'off',
    'react/jsx-wrap-multilines': [
      'warn',
      {
        declaration: 'parens-new-line',
        assignment: 'parens-new-line',
        return: 'parens-new-line',
        arrow: 'parens-new-line',
        condition: 'parens-new-line',
        logical: 'parens-new-line',
        prop: 'parens-new-line',
      },
    ],
    'react/no-set-state': 'off',
    'react/destructuring-assignment': 'off',
    'react/require-optimization': 'off',
    'react/static-property-placement': 'off',
    'react/jsx-child-element-spacing': 'off',
    semi: ['warn', 'never'],
  },
  overrides: [
    {
      files: ['testcafe/*.js', 'quality_assurance/*.js'],
      rules: {
        'jest/expect-expect': 'off',
        'jest/lowercase-name': 'off',
        'jest/no-test-callback': 'off',
        'jest/prefer-expect-assertions': 'off',
        'jest/require-top-level-describe': 'off',
        'jest/no-done-callback': 'off',
      },
    },
    {
      files: ['**/pages/Styleguide/**/*'],
      rules: {
        'react/no-unescaped-entities': 'off',
        'react/jsx-child-element-spacing': 'off',
      },
    },
    {
      files: ['**/*.ts?(x)'],
      plugins: ['@typescript-eslint/eslint-plugin'],
      extends: ["plugin:@typescript-eslint/recommended"],
      rules: {
        'react/prop-types': 'off',
      },
    },
  ],
  settings: {
    'import/resolver': {
      node: {
        extensions: ['.js', '.jsx', '.ts', '.jsx', '.tsx'],
        paths: ['.'],
        moduleDirectory: ['node_modules', 'src'],
      },
    },
    react: {
      version: 'detect',
    },
  },
}

const newConfig = {
  ...comonConfig,
  extends: [...comonConfig.extends, 'plugin:testing-library/react'],
  rules: {
    ...comonConfig.rules,
    complexity: ['error', 20],
    'max-depth': ['error', { max: 4 }],
    'max-lines': ['error', { max: 300, skipBlankLines: true }],
    'max-statements': ['error', 15],
    'max-lines-per-function': ['error', 50],
    'max-params': ['error', 5],
    'max-nested-callbacks': ['error', 5],
  },
  overrides: [
    ...comonConfig.overrides,
    {
      files: ['./src/**/*.[jt]sx'],
      rules: {
        'max-lines-per-function': ['error', 150],
      },
    },
    {
      files: ['./src/**/__tests__/**/*.[jt]s?(x)', '.src/**/?(*.)+(spec|test).[jt]s?(x)'],
      extends: ['plugin:testing-library/react'],
      rules: {
        'max-lines-per-function': ['error', 300],
        'max-nested-callbacks': ['error', 50],
      },
    },
  ],
}

const config = () => {
  return newStrictConfig ? newConfig : comonConfig
}

module.exports = config()
