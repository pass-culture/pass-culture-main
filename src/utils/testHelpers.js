import { render } from '@testing-library/react'
import omit from 'lodash.omit'
import sass from 'node-sass'

export const queryCallbacks = {
  // From the 4th tips of this article: https://www.polvara.me/posts/five-things-you-didnt-know-about-testing-library/
  // This allow to search text including children like "Hello world!" in :
  // <button>Hello: <span>world!</span></button>
  // basic screen.queryByText would not match
  queryByTextWithChildren: (searchString, leafOnly = true) => {
    return (_content, node) => {
      const hasText = node =>
        node.textContent === searchString || node.textContent.match(searchString)
      const nodeHasText = hasText(node)

      // Parent node also have 'searchString' as textContent.
      // We only wanna return true for the leafs.
      const childrenDontHaveText = Array.from(node.children).every(child => !hasText(child))

      return nodeHasText && (!leafOnly || childrenDontHaveText)
    }
  },
}

export function queryByTextTrimHtml(screen, searchString, options = {}) {
  const { leafOnly } = options
  return screen.queryByText(
    queryCallbacks.queryByTextWithChildren(searchString, leafOnly),
    omit(options, 'leafOnly')
  )
}

export function renderWithStyles(ui, options = {}) {
  const view = render(ui, {
    ...omit(options, 'stylesheet'),
  })
  if (options.stylesheet) {
    const stylesData = `
    @import 'src/styles/variables/index.scss';
    @import 'src/styles/${options.stylesheet}';
    `
    const styles = sass.renderSync({ data: stylesData })

    const styleElement = document.createElement('style')
    styleElement.innerHTML = styles.css.toString()
    document.body.appendChild(styleElement)
    document.body.appendChild(view.container)
  }

  return view
}
