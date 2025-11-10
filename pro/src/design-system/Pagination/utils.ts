const NB_PAGES_AROUND_CURRENT_DESKTOP = 2
const NB_PAGES_AROUND_CURRENT_MOBILE = 1
const NB_MINIMUM_TO_PAGINATE = 8

/**
 * Generates an array of page numbers to display near the current page,
 * excluding the first and last page (which are always shown separately).
 *
 * When the total number of pages is less than the minimum pagination threshold,
 * returns all intermediate pages except the first and last.
 * Otherwise, generates a range of pages centered around the current page,
 * taking into account the "around" count depending on mobile or desktop.
 *
 * @param {number} currentPage - The current active page number.
 * @param {number} pageCount - The total number of pages.
 * @param {{ isMobile?: boolean }} options - Options object.
 * @param {boolean} [options.isMobile=false] - Whether in mobile view mode.
 * @returns {number[]} The array of visible (central) page numbers, not including the first or last page.
 */
export const generateNearestPages = (
  currentPage: number,
  pageCount: number,
  { isMobile = false }: { isMobile?: boolean } = {}
) => {
  if (pageCount < NB_MINIMUM_TO_PAGINATE) {
    return Array.from({ length: pageCount }, (_, index) => index + 2).slice(
      0,
      -2
    )
  }

  // Generates the current page array and pages "around"
  // We still display 1st and last page, but we need to generate also "center" pages
  // Ex: for currentPage = 8 (with 2 pages around) we want to have [6, 7, (8), 9, 10]
  // But we must handles with the bounds ;
  //  - if we're on page 8/8 then we want [3, 4, 5, 6, 7]
  //  - if we're on page 2/8 then we want [(2), 3, 4, 5, 6]
  const nbPagesAroundCurrent = isMobile
    ? NB_PAGES_AROUND_CURRENT_MOBILE
    : NB_PAGES_AROUND_CURRENT_DESKTOP
  let leftBound = currentPage - nbPagesAroundCurrent
  let rightBound = currentPage + nbPagesAroundCurrent
  const distance = rightBound - leftBound

  if (leftBound < 2) {
    leftBound = 2
    rightBound = leftBound + distance
  } else if (rightBound > pageCount - 1) {
    rightBound = pageCount - 1
    leftBound = rightBound - distance
  }

  const nearestPages = Array.from(
    { length: rightBound - leftBound + 1 },
    (_, index) => leftBound + index
  )

  return nearestPages
}
