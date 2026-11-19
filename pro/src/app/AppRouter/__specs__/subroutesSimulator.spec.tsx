import { matchRoutes } from 'react-router'

import { inscriptionPreparationRoutes } from '../routes/inscriptionPreparation'

describe('inscriptionPreparationRoutes', () => {
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
        [
          {
            path: '/inscription/preparation',
            children: inscriptionPreparationRoutes,
          },
        ],
        path
      )
    ).not.toBeNull()
  })
})
