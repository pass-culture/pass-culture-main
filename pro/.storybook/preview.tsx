import '../src/styles/index.scss'

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
