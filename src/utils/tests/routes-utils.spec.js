/* eslint no-console: 0, max-nested-callbacks: 0 */
import { getReactRoutes, getMainMenuItems } from '../routes-utils'

describe('getReactRoutes', () => {
  it('filtre les routes pour react-router', () => {
    const values = [
      { path: '/' },
      { path: '/toto' },
      { path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'maitlo:mail.cool' },
    ]
    const results = getReactRoutes(values)
    const expected = [
      { exact: true, path: '/' },
      { exact: true, path: '/toto' },
      { exact: true, path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' },
      null,
    ]
    expect(results).toStrictEqual(expected)
  })
})

describe('getMainMenuItems', () => {
  it('filtre les routes pour react-router', () => {
    const values = [
      { path: '/' },
      { icon: '/' },
      { path: '/toto' },
      { icon: 'toto', path: '/toto/:vars?' },
      { href: '/toto/:vars?', icon: 'toto' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { icon: 'toto', path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'mailto:mail.cool' },
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    const results = getMainMenuItems(values)
    const expected = [
      null,
      null,
      null,
      { icon: 'toto', path: '/toto' },
      { href: '/toto/:vars?', icon: 'toto' },
      null,
      { icon: 'toto', path: '/toto' },
      null,
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    expect(results).toStrictEqual(expected)
  })
})
