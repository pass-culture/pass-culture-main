import { matchRoutes } from 'react-router'

import { routesWelcomeCarousel } from '../subroutesWelcomeCarousel'

describe('routesWelcomeCarousel', () => {
  it.each([
    '/bienvenue',
    '/bienvenue/publics',
    '/bienvenue/offres-jeunes',
    '/bienvenue/offres-scolaires',
    '/bienvenue/avantages',
    '/bienvenue/prochaines-etapes',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes(
        [{ path: '/bienvenue', children: routesWelcomeCarousel }],
        path
      )
    ).not.toBeNull()
  })
})
