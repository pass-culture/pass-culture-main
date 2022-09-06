import { fireEvent } from '@testing-library/react'
import omit from 'lodash.omit'

export const queryCallbacks = {
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
    omit(options, 'leafOnly')
  )
}

export const getNthCallNthArg = (mockedFunction, nthCall, nthArg = 1) =>
  mockedFunction.mock.calls[nthCall - 1][nthArg - 1]

export const clearInputText = input =>
  fireEvent.change(input, { target: { value: '' } })
