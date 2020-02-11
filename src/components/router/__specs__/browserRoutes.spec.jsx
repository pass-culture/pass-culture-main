import getBrowserRoutes from '../getBrowserRoutes'

describe('filterRoutes', () => {
  it('filters routes pour react-router', () => {
    const routes = [
      { path: '/' },
      { path: '/toto' },
      { path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?', sensitive: true },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?', sensitive: false },
      { href: 'maitlo:mail.cool' },
    ]
    const browserRoutes = getBrowserRoutes(routes)
    const expected = [
      { exact: true, path: '//:menu(menu)?', sensitive: true },
      { exact: true, path: '/toto/:menu(menu)?', sensitive: true },
      { exact: true, path: '/toto/:vars?/:menu(menu)?', sensitive: true },
      { exact: true, path: '/toto/:vars?/vars2?/:menu(menu)?', sensitive: true },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?/:menu(menu)?', sensitive: false },
    ]
    expect(browserRoutes).toStrictEqual(expected)
  })
})
