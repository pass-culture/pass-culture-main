import DiscoveryContainer from '../../../../pages/discovery/DiscoveryContainer'
import MyFavoritesContainer from '../../../../pages/my-favorites/MyFavoritesContainer'
import MyBookingsContainer from '../../../../pages/my-bookings/MyBookingsContainer'
import ProfileContainer from '../../../../pages/profile/ProfileContainer'
import SearchContainer from '../../../../pages/search/SearchContainer'
import routes from '../../../../router/routes'
import { getMenuItemsFromRoutes } from '../getMenuItems'

describe('getMenuItemsFromRoutes', () => {
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
    const items = getMenuItemsFromRoutes(testRoutes)
    const expected = [
      { icon: 'toto', path: '/toto' },
      { href: '/toto/:vars?', icon: 'toto' },
      { icon: 'toto', path: '/toto' },
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    expect(items).toStrictEqual(expected)
  })

  it('should filter routes for menu from featured routes', () => {
    // when
    const items = getMenuItemsFromRoutes(routes)
    const expected = [
      {
        component: DiscoveryContainer,
        icon: 'offres-w',
        path: '/decouverte',
        title: 'Les offres',
      },
      {
        component: SearchContainer,
        icon: 'search-w',
        path: '/recherche',
        title: 'Recherche',
      },
      {
        component: MyBookingsContainer,
        icon: 'calendar-w',
        path: '/reservations',
        title: 'Mes réservations',
      },
      {
        component: MyFavoritesContainer,
        featureName: 'FAVORITE_OFFER',
        icon: 'like-w',
        path: '/favoris',
        title: 'Mes favoris',
      },
      {
        component: ProfileContainer,
        icon: 'user-w',
        path: '/profil',
        title: 'Mon compte',
      },
      {
        href: 'https://aide.passculture.app/fr/category/18-ans-1dnil5r/',
        icon: 'help-w',
        target: '_blank',
        title: 'Aide',
      },
      {
        href:
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
