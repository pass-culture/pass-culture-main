import { matchRoutes } from 'react-router'

import { routesEcoDesign } from '../subroutesEcoDesignMap'

describe('routesEcoDesign', () => {
  it.each([
    '/ecoconception',
    '/ecoconception/politique',
    '/ecoconception/declaration',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes([{ path: '/ecoconception', children: routesEcoDesign }], path)
    ).not.toBeNull()
  })
})
