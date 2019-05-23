import { getMenuItemIdFromPathname, getMenuItemPathTo } from '../utils'

describe('src | components | menu | utils', () => {
  describe('getMenuItemIdFromPathname', () => {
    it('is active, return location path with search query', () => {
      const currenUrlLocation = {
        pathname: 'base/path/to/current/page',
        search: '?search=current_active_page_with_searchquery',
      }
      const item = { path: 'base/path/to/current/page' }
      const result = getMenuItemPathTo(currenUrlLocation, item)

      const expected =
        'base/path/to/current/page?search=current_active_page_with_searchquery'
      expect(result).toStrictEqual(expected)
    })

    it(`is not active, return item's path without current search query`, () => {
      const currenUrlLocation = {
        pathname: 'base/path/to/current/page',
        search: '?search=current_active_page_with_searchquery',
      }
      const item = { path: 'base/path/to/another/page' }
      const result = getMenuItemPathTo(currenUrlLocation, item)

      const expected = 'base/path/to/another/page'
      expect(result).toStrictEqual(expected)
    })
  })

  describe('getMenuItemIdFromPathname', () => {
    it('return a string based on destination for menu item', () => {
      // given
      const pathto = '/base/string/path/to'
      const prefix = 'this-is-the-prefix-for'

      // when
      const result = getMenuItemIdFromPathname(pathto, prefix)

      // then
      const expected = 'this-is-the-prefix-for-base-button'
      expect(result).toStrictEqual(expected)
    })

    it('throw an error if no valid pathto arg', () => {
      // given
      const pathto = null
      const prefix = 'this-is-the-prefix-for'

      // then
      expect(() => getMenuItemIdFromPathname(pathto, prefix)).toThrow()
    })

    it('throw an error if no valid prefix arg', () => {
      // given
      const pathto = '/base/string/path/to'
      const prefix = ['not a string']

      // then
      expect(() => getMenuItemIdFromPathname(pathto, prefix)).toThrow()
    })

    it('return a string based on destination for menu item when path contains a search query', () => {
      // given
      const pathto = '/base/string/path/to?query=any'
      const prefix = 'this-is-the-prefix-for'

      // when
      const result = getMenuItemIdFromPathname(pathto, prefix)

      // then
      const expected = 'this-is-the-prefix-for-base-button'
      expect(result).toStrictEqual(expected)
    })

    it('return a string based on destination for menu item when path contains a search query when route contains only one path', () => {
      // given
      const pathto = '/base'
      const prefix = 'this-is-the-prefix-for'

      // when
      const result = getMenuItemIdFromPathname(pathto, prefix)

      // then
      const expected = 'this-is-the-prefix-for-base-button'
      expect(result).toStrictEqual(expected)
    })
  })
})
