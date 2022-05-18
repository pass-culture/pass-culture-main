import '!style-loader!css-loader!resolve-url-loader!sass-loader!../src/styles/index.scss'

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
      order: ['ui-kit', 'components'],
    },
  },
}
