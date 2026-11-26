import { matchRoutes } from 'react-router'

import { inscriptionRoutes } from '../routes/inscription'

describe('inscriptionRoutes', () => {
  it.each([
    '/inscription',
    '/inscription/compte/creation',
    '/inscription/compte/confirmation',
    '/inscription/compte/confirmation/token-123',
    '/inscription/validation/token-123',
    '/inscription/confirmation',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes([{ path: '/inscription', children: inscriptionRoutes }], path)
    ).not.toBeNull()
  })
})
