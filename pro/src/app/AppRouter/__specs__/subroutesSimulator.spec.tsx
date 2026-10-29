import { matchRoutes } from 'react-router'

import { routesSimulator } from '../subroutesSimulator'

describe('routesSimulator', () => {
  it.each([
    '/inscription/preparation',
    '/inscription/preparation/siret',
    '/inscription/preparation/accueil-public',
    '/inscription/preparation/activite',
    '/inscription/preparation/publics',
    '/inscription/preparation/resultats',
    '/inscription/preparation/email',
    '/inscription/preparation/email-confirmation',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes(
        [{ path: '/inscription/preparation', children: routesSimulator }],
        path
      )
    ).not.toBeNull()
  })
})
