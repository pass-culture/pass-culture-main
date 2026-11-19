import { matchRoutes } from 'react-router'

import { ecoconceptionRoutes } from '../routes/ecoconception'

describe('ecoconceptionRoutes', () => {
  it.each([
    '/ecoconception',
    '/ecoconception/politique',
    '/ecoconception/declaration',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes(
        [{ path: '/ecoconception', children: ecoconceptionRoutes }],
        path
      )
    ).not.toBeNull()
  })
})
