import type { StorybookConfig } from '@storybook/react-vite'

const config: StorybookConfig = {
  stories: [
    '../src/ui-kit/Icons/Icons.stories.tsx',
    '../src/**/*.stories.@(js|jsx|ts|tsx)',
  ],
  addons: [
    '@storybook/addon-a11y',
    '@storybook/addon-controls',
    '@storybook/preset-scss',
    'storybook-addon-react-router-v6',
  ],
  staticDirs: ['../src/public'],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  docs: {
    autodocs: true,
  },
  // Temporary plugin to expose env variables in the `process.env` object
  // Once we move to Vitest we should remove this plugin and use the
  // `import.meta.env` object instead
  async viteFinal(config) {
    config.define = { 'process.env': process.env }
    return config
  },
}

export default config
