import { generateNearestPages } from './utils'

describe('generateNearestPages', () => {
  describe('on desktop', () => {
    it.each([
      { currentPage: 3, pageCount: 6, expected: [2, 3, 4, 5] },
      {
        currentPage: 9,
        pageCount: 18,
        expected: [7, 8, 9, 10, 11],
      },
      {
        currentPage: 16,
        pageCount: 18,
        expected: [13, 14, 15, 16, 17],
      },
    ])('should return $expected for page $currentPage/$pageCount on desktop', ({
      currentPage,
      pageCount,
      expected,
    }) => {
      const result = generateNearestPages(currentPage, pageCount)
      expect(result).toEqual(expected)
    })
  })

  describe('on mobile', () => {
    it.each([
      { currentPage: 3, pageCount: 6, expected: [2, 3, 4, 5] },
      { currentPage: 9, pageCount: 18, expected: [8, 9, 10] },
      { currentPage: 6, pageCount: 8, expected: [5, 6, 7] },
    ])('should return $expected for page $currentPage/$pageCount on mobile', ({
      currentPage,
      pageCount,
      expected,
    }) => {
      const result = generateNearestPages(currentPage, pageCount, {
        isMobile: true,
      })
      expect(result).toEqual(expected)
    })
  })
})
