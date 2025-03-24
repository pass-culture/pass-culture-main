import type { StorybookConfig } from '@storybook/react-vite'

const config: StorybookConfig = {
  stories: [
    '../src/ui-kit/Icons/Icons.stories.tsx',
    '../src/**/*.mdx',
    '../src/**/*.stories.@(js|jsx|ts|tsx)',
  ],
  addons: [
    '@storybook/addon-a11y',
    '@storybook/addon-controls',
    '@storybook/addon-docs',
    'storybook-addon-remix-react-router',
  ],
  typescript: {
    reactDocgen: 'react-docgen-typescript',
  },
  staticDirs: ['../src/public'],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  async viteFinal(config) {
    if (config.build) {
      //  Make sure that the <use> content in svgs is not inlined which is forbidden by some browsers
      config.build.assetsInlineLimit = 0
    }
    return config
  },
  docs: {
    defaultName: 'Documentation',
  },
}

export default config
