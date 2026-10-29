import { matchRoutes } from 'react-router'

import { routesSignup } from '../subroutesSignupMap'

describe('routesSignup', () => {
  it.each([
    '/inscription',
    '/inscription/compte/creation',
    '/inscription/compte/confirmation',
    '/inscription/compte/confirmation/token-123',
    '/inscription/validation/token-123',
    '/inscription/confirmation',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes([{ path: '/inscription', children: routesSignup }], path)
    ).not.toBeNull()
  })
})
