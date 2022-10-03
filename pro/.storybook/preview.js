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
      method: (a, b) =>
      a[1].kind === b[1].kind ? 0 : a[1].id.localeCompare(b[1].id, undefined, { numeric: true }),
    },
  },
}
