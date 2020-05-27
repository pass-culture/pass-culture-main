import getBrowserRoutes from '../getBrowserRoutes'

describe('filterRoutes', () => {
  it('filters routes pour react-router', () => {
    // Given
    const routes = [
      { path: '/' },
      { path: '/toto' },
      { path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?', sensitive: true },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?', sensitive: false },
      { href: 'maitlo:mail.cool' },
    ]

    // When
    const browserRoutes = getBrowserRoutes(routes)

    // Then
    expect(browserRoutes).toStrictEqual([
      { exact: true, path: '/', sensitive: true },
      { exact: true, path: '/toto', sensitive: true },
      { exact: true, path: '/toto/:vars?', sensitive: true },
      { exact: true, path: '/toto/:vars?/vars2?', sensitive: true },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?', sensitive: false },
    ])
  })
})
