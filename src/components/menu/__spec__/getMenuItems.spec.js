import getMenuItems from '../getMenuItems'
import DiscoveryContainer from '../../pages/discovery/DiscoveryContainer'
import FavoritesPage from '../../pages/FavoritesPage'
import MyBookingsContainer from '../../pages/my-bookings/MyBookingsContainer'
import ProfilePage from '../../pages/profile'
import SearchContainer from '../../pages/search/SearchContainer'
import routes from '../../router/routes'

describe('getMenuItems', () => {
  it('should filter routes for menu from mock', () => {
    const testRoutes = [
      { path: '/' },
      { path: '/toto' },
      { icon: 'toto', path: '/toto/:vars?' },
      { href: '/toto/:vars?', icon: 'toto' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { icon: 'toto', path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'mailto:mail.cool' },
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    const items = getMenuItems(testRoutes)
    const expected = [
      { icon: 'toto', key: '/toto', path: '/toto' },
      { href: '/toto/:vars?', icon: 'toto', key: '/toto/:vars?' },
      { icon: 'toto', key: '/toto', path: '/toto' },
      { href: 'mailto:mail.cool', icon: 'toto', key: 'mailto:mail.cool' },
    ]
    expect(items).toStrictEqual(expected)
  })

  it('should filter routes for menu from featured routes', () => {
    // when
    const items = getMenuItems(routes)
    const expected = [
      {
        component: DiscoveryContainer,
        icon: 'offres-w',
        key: '/decouverte',
        path: '/decouverte',
        title: 'Les offres',
      },
      {
        component: SearchContainer,
        icon: 'search-w',
        key: '/recherche',
        path: '/recherche',
        title: 'Recherche',
      },
      {
        component: MyBookingsContainer,
        icon: 'calendar-w',
        key: '/reservations',
        path: '/reservations',
        title: 'Mes réservations',
      },
      {
        component: FavoritesPage,
        featureName: 'FAVORITE_OFFER',
        key: '/favoris',
        icon: 'like-w',
        path: '/favoris',
        title: 'Mes préférés',
      },
      {
        component: ProfilePage,
        icon: 'user-w',
        key: '/profil',
        path: '/profil',
        title: 'Mon compte',
      },
      {
        href: 'https://docs.passculture.app/experimentateurs',
        icon: 'help-w',
        key: 'https://docs.passculture.app/experimentateurs',
        target: '_blank',
        title: 'Aide',
      },
      {
        href:
          'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture',
        key:
          'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture',
        icon: 'txt-w',
        target: '_blank',
        title: 'Mentions légales',
      },
    ]

    // then
    expect(items).toStrictEqual(expected)
  })
})
