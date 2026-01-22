import path from 'node:path'
import type { StorybookConfig } from '@storybook/react-vite'
import { mergeConfig } from 'vite'

const config: StorybookConfig = {
  stories: [
    '../src/ui-kit/Icons/Icons.stories.tsx',
    '../src/**/*.mdx',
    '../src/**/*.stories.@(js|jsx|ts|tsx)',
  ],
  addons: [
    '@storybook/addon-a11y',
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
    const customConfig = mergeConfig(config, {
      resolve: {
        alias: [
          {
            find: '@/apiClient/api',
            replacement: path.resolve(
              __dirname,
              '../src/apiClient/__mocks__/api.ts'
            ),
          },
        ],
      },
    })

    if (customConfig.build) {
      customConfig.build.assetsInlineLimit = 0
    }

    return customConfig
  },
  docs: {
    defaultName: 'Documentation',
  },
}

// biome-ignore lint/style/noDefaultExport: No other way to export a Storybook config.
export default config
