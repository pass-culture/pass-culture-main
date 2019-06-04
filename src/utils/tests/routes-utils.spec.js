// jest --env=jsdom ./src/utils/tests/routes-utils --watch
import { filterRoutes, getMainMenuItems } from '../routes-utils'

import routes from '../routes'

import DiscoveryPage from '../../components/pages/discovery'
import FavoritesPage from '../../components/pages/FavoritesPage'
import MyBookingsPage from '../../components/pages/my-bookings'
import ProfilePage from '../../components/pages/profile'
import { SearchContainer as Search } from '../../components/pages/search/Search'
import { SUPPORT_EMAIL, SUPPORT_EMAIL_SUBJECT } from '../config'

describe('filterRoutes', () => {
  it('filter routes pour react-router', () => {
    const values = [
      { path: '/' },
      { path: '/toto' },
      { path: '/toto/:vars?' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { exact: false, path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'maitlo:mail.cool' },
    ]
    const result = filterRoutes(values)
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
      null, // Typeform
      {
        component: DiscoveryPage,
        disabled: false,
        icon: 'offres-w',
        path: '/decouverte',
        title: 'Les offres',
      },
      {
        component: Search,
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
        href: `mailto:${SUPPORT_EMAIL}?subject=${SUPPORT_EMAIL_SUBJECT}`,
        icon: 'mail-w',
        title: 'Nous contacter',
      },
      {
        disabled: false,
        href:
          'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture',
        icon: 'txt-w',
        target: '_blank',
        title: 'Mentions Légales',
      },
    ]

    // then
    expect(result).toEqual(expected)
  })
})
