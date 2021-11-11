import getThumbUrl from '../getThumbUrl'

let mockPath = ''
jest.mock('../config', () => ({
  get OBJECT_STORAGE_URL() {
    return mockPath
  },
}))

describe('src | helpers | getThumbUrl', () => {
  it.each`
    thumbUrl               | urlPrefix    | expected
    ${undefined}           | ${'newpath'} | ${undefined}
    ${'oldpath/thumbs/ID'} | ${undefined} | ${'oldpath/thumbs/ID'}
    ${'oldpath/thumbs/ID'} | ${'newpath'} | ${'newpath/thumbs/ID'}
    ${'/thumbs/ID'}        | ${'newpath'} | ${'newpath/thumbs/ID'}
    ${'newpath/thumbs/ID'} | ${'newpath'} | ${'newpath/thumbs/ID'}
  `(
    'should parse the image url from the thumbUrl=$thumbUrl stored in Algolia',
    ({ thumbUrl, urlPrefix, expected }) => {
      mockPath = urlPrefix
      expect(getThumbUrl(thumbUrl)).toBe(expected)
    }
  )
})
