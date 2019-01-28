// jest --env=jsdom ./src/utils/tests/routes-utils --watch
import { getReactRoutes, getMainMenuItems } from '../routes-utils'

import routes from '../routes'

import SearchPage from '../../components/pages/SearchPage'
import MyBookingsPage from '../../components/pages/my-bookings'
import DiscoveryPage from '../../components/pages/discovery'
import FavoritesPage from '../../components/pages/FavoritesPage'

import ProfilePage from '../../components/pages/profile'
import TermsPage from '../../components/pages/TermsPage'

describe('getReactRoutes', () => {
  it('filter routes pour react-router', () => {
    const values = [
      { path: '/' },
      { path: '/toto' },
      { path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'maitlo:mail.cool' },
    ]
    const result = getReactRoutes(values)
    const expected = [
      { exact: true, path: '/' },
      { exact: true, path: '/toto' },
      { exact: true, path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' },
      null,
    ]
    expect(result).toStrictEqual(expected)
  })
})

describe('getMainMenuItems', () => {
  it('filter routes for react-router', () => {
    const values = [
      { path: '/' },
      { icon: '/' },
      { path: '/toto' },
      { icon: 'toto', path: '/toto/:vars?' },
      { href: '/toto/:vars?', icon: 'toto' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { icon: 'toto', path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'mailto:mail.cool' },
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    const result = getMainMenuItems(values)
    const expected = [
      null,
      null,
      null,
      { icon: 'toto', path: '/toto' },
      { href: '/toto/:vars?', icon: 'toto' },
      null,
      { icon: 'toto', path: '/toto' },
      null,
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    expect(result).toStrictEqual(expected)
  })

  it('should filter routes from webapp', () => {
    // when
    const result = getMainMenuItems(routes)
    const expected = [
      null, // redirect
      null, // BetaPage
      null, // Signin/Connexion
      null, // Signup/Inscription
      null, // ForgotPasswordPage
      null, // Activation
      {
        component: DiscoveryPage,
        disabled: false,
        icon: 'offres-w',
        path: '/decouverte',
        title: 'Les offres',
      },
      {
        component: SearchPage,
        disabled: false,
        icon: 'search-w',
        path: '/recherche',
        title: 'Recherche',
      },
      {
        component: MyBookingsPage,
        disabled: false,
        icon: 'calendar-w',
        path: '/reservations',
        title: 'Mes Réservations',
      },
      {
        component: FavoritesPage,
        disabled: true,
        icon: 'like-w',
        path: '/favoris',
        title: 'Mes Préférés',
      },
      {
        component: ProfilePage,
        disabled: false,
        icon: 'user-w',
        path: '/profil',
        title: 'Mon Profil',
      },

      {
        disabled: false,
        href: 'mailto:pass@culture.gouv.fr',
        icon: 'mail-w',
        title: 'Nous contacter',
      },
      {
        component: TermsPage,
        disabled: false,
        icon: 'txt-w',
        path: '/mentions-legales',
        title: 'Mentions Légales',
      },
    ]

    // then
    expect(result).toEqual(expected)
  })
})
