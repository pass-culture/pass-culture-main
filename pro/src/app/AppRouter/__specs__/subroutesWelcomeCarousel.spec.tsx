import { matchRoutes } from 'react-router'

import { bienvenueRoutes } from '../routes/bienvenue'

describe('bienvenueRoutes', () => {
  it.each([
    '/bienvenue',
    '/bienvenue/publics',
    '/bienvenue/offres-jeunes',
    '/bienvenue/offres-scolaires',
    '/bienvenue/avantages',
    '/bienvenue/prochaines-etapes',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes([{ path: '/bienvenue', children: bienvenueRoutes }], path)
    ).not.toBeNull()
  })
})
