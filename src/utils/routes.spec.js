/* eslint no-console: 0, max-nested-callbacks: 0 */
import { getReactRoutes } from './routes'

describe('getMainMenuItems', () => {
  it('retourne uniquement les objets pour le MainMenu', () => {
    const values = [
      {
        path: '/',
      },
      {
        path: '/toto/is/awesome?',
      },
      {
        href: 'mailto:http://cool.com',
      },
    ]
    const results = getReactRoutes(values)
    const expected = [
      {
        exact: true,
        key: '/',
        path: '/',
      },
      {
        exact: true,
        key: '/toto/is/awesome?',
        path: '/toto/is/awesome?',
      },
    ]
    expect(expected).toStrictEqual(results)
  })
})
