import getBrowserRoutes from '../getBrowserRoutes'

describe('filterRoutes', () => {
  it('filters routes pour react-router', () => {
    const routes = [
      { path: '/' },
      { path: '/toto' },
      { path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'maitlo:mail.cool' },
    ]
    const browserRoutes = getBrowserRoutes(routes)
    const expected = [
      { exact: true, path: '//:menu(menu)?' },
      { exact: true, path: '/toto/:menu(menu)?' },
      { exact: true, path: '/toto/:vars?/:menu(menu)?' },
      { exact: true, path: '/toto/:vars?/vars2?/:menu(menu)?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?/:menu(menu)?' }
    ]
    expect(browserRoutes).toStrictEqual(expected)
  })
})
