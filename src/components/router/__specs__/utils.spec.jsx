import { extendRoutesWithExact, removeDisabledRoutes, removeHrefRoutes } from '../utils'
import { pipe } from '../../../utils/functionnals'

describe('filterRoutes', () => {
  it('filters routes pour react-router', () => {
    const routes = [
      { path: '/' },
      { path: '/toto' },
      { path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' },
      { disabled: true, path: '/inscription' },
      { href: 'maitlo:mail.cool' },
    ]
    const result = pipe(
      removeHrefRoutes,
      removeDisabledRoutes,
      extendRoutesWithExact,
    )(routes)
    const expected = [
      { exact: true, path: '/' },
      { exact: true, path: '/toto' },
      { exact: true, path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' }
    ]
    expect(result).toStrictEqual(expected)
  })
})
