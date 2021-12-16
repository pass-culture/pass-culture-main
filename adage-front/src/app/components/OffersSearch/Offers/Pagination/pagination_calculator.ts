export const getPages = (
  currentRefinement: number,
  nbPages: number
): Array<string | number> => {
  let pages: (number | string)[] = [1]
  const pagesToDisplay = [
    currentRefinement - 1,
    currentRefinement,
    currentRefinement + 1,
  ].filter(page => page > 1 && page < nbPages)

  if (pagesToDisplay[0] > 2) {
    pages.push('...')
    pages.push(...pagesToDisplay)
    if (pagesToDisplay[pagesToDisplay.length - 1] < nbPages - 1) {
      pages.push('...')
    }
    pages.push(nbPages)
  } else if (nbPages > 3) {
    pages.push(...pagesToDisplay)
    if (pagesToDisplay[pagesToDisplay.length - 1] < nbPages - 1) {
      pages.push('...')
    }
    pages.push(nbPages)
  } else {
    pages = new Array(nbPages).fill(null).map((_, index) => index + 1)
  }
  return pages
}
