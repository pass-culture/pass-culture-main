export const parameters = {
  backgrounds: {
    grid: {
      cellSize: 8,
    },
  },
  controls: {
    expanded: true,
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

export const tags = ['autodocs']
