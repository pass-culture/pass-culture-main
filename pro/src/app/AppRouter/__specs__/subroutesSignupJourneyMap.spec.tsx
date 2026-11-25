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

  it.each([
    ['recherche', 'Offerer'],
    ['rattachement', 'Offerers'],
    ['rattachement/confirmation-rattachement', 'ConfirmedAttachment'],
    ['identification', 'OffererAuthentication'],
    ['activite', 'Activity'],
    ['confirmation', 'Validation'],
  ])('should load the component for %s', async (path, componentName) => {
    const lazy = routesSignupJourney.find((route) => route.path === path)?.lazy
    if (typeof lazy !== 'function') {
      throw new Error(`Missing lazy route for ${path}`)
    }

    expect((await lazy()).Component).toHaveProperty('name', componentName)
  })
})
