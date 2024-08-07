import '../src/styles/index.scss'
import React from 'react'

import { Preview } from '@storybook/react'

const preview: Preview = {
  decorators: [
    (Story) => (
      <div data-theme-storybook="blue">
        <Story />
      </div>
    ),
  ],
}

export default preview

export const parameters = {
  backgrounds: {
    grid: {
      cellSize: 8,
    },
  },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
  options: {
    storySort: {
      order: ['icons', 'ui-kit', 'components'],
      method: 'alphabetical',
    },
  },
}
