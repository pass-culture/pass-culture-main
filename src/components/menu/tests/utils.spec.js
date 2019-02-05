// jest --env=jsdom ./src/components/menu/tests/utils --watch
import { getMenuItemIdFromPathname } from '../utils'

describe('src | components | menu | utils', () => {
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
})
