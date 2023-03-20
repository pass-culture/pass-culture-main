/* istanbul ignore file */

const queryCallbacks = {
  // From the 4th tips of this article: https://www.polvara.me/posts/five-things-you-didnt-know-about-testing-library/
  // This allow to search text including children like "Hello world!" in :
  // <button>Hello: <span>world!</span></button>
  // basic screen.queryByText would not match
  queryByTextWithChildren: (searchString, leafOnly = true) => {
    return (_content, node) => {
      const hasText = node => {
        const normalizedText = node.textContent.replace(/\s/g, ' ')
        return (
          normalizedText === searchString || normalizedText.match(searchString)
        )
      }
      const nodeHasText = hasText(node)

      // Parent node also have 'searchString' as textContent.
      // We only wanna return true for the leafs.
      const childrenDontHaveText = Array.from(node.children).every(
        child => !hasText(child)
      )

      return nodeHasText && (!leafOnly || childrenDontHaveText)
    }
  },
}

export function queryByTextTrimHtml(screen, searchString, options = {}) {
  const { leafOnly } = options
  return screen.queryByText(
    queryCallbacks.queryByTextWithChildren(searchString, leafOnly),
    // remove key leafOnly from options
    Object.keys(options).reduce((acc, cur) => {
      return cur !== 'leafOnly' ? { ...acc, [cur]: options[cur] } : acc
    }, {})
  )
}

export const getNthCallNthArg = (mockedFunction, nthCall, nthArg = 1) =>
  mockedFunction.mock.calls[nthCall - 1][nthArg - 1]
