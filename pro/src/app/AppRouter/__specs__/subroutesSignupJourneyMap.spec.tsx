import { matchRoutes } from 'react-router'

import { routesSignupJourney } from '../subroutesSignupJourneyMap'

describe('routesSignupJourney', () => {
  it.each([
    '/inscription/structure/recherche',
    '/inscription/structure/rattachement',
    '/inscription/structure/rattachement/confirmation-rattachement',
    '/inscription/structure/identification',
    '/inscription/structure/activite',
    '/inscription/structure/confirmation',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes(
        [{ path: '/inscription/structure', children: routesSignupJourney }],
        path
      )
    ).not.toBeNull()
  })
})
