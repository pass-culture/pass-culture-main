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
  // biome-ignore lint/suspicious/useAwait: TODO (igabriele, 2025-08-05): Suspicious indeed, not sure why it is needed.
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

// biome-ignore lint/style/noDefaultExport: No other way to export a Storybook config.
export default config
