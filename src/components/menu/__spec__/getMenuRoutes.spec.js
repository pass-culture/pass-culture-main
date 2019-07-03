import getMenuRoutes from '../getMenuRoutes'
import DiscoveryPage from '../../pages/discovery'
import MyBookingsContainer from '../../pages/my-bookings'
import ProfilePage from '../../pages/profile'
import SearchContainer from '../../pages/search/SearchContainer'
import { getFeaturedRoutes } from '../../router/utils'

describe('getMenuRoutes', () => {
  it('should filter routes for menu from mock', () => {
    const values = [
      { path: '/' },
      { path: '/toto' },
      { icon: 'toto', path: '/toto/:vars?' },
      { href: '/toto/:vars?', icon: 'toto' },
      { exact: true, path: '/toto/:vars?/vars2?' },
      { icon: 'toto', path: '/toto/:vars?/:vars2?/:vars3?' },
      { href: 'mailto:mail.cool' },
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    const result = getMenuRoutes(values)
    const expected = [
      { icon: 'toto', path: '/toto' },
      { href: '/toto/:vars?', icon: 'toto' },
      { icon: 'toto', path: '/toto' },
      { href: 'mailto:mail.cool', icon: 'toto' },
    ]
    expect(result).toStrictEqual(expected)
  })

  it('should filter routes for menu from featured routes', () => {
    // when
    const features = [{ name: 'WEBAPP_SIGNUP' }]
    const featuredRoutes = getFeaturedRoutes(features)
    const result = getMenuRoutes(featuredRoutes)
    const expected = [
      {
        component: DiscoveryPage,
        disabled: false,
        exact: true,
        icon: 'offres-w',
        path: '/decouverte',
        title: 'Les offres',
      },
      {
        component: SearchContainer,
        disabled: false,
        exact: true,
        icon: 'search-w',
        path: '/recherche',
        title: 'Recherche',
      },
      {
        component: MyBookingsContainer,
        disabled: false,
        exact: true,
        icon: 'calendar-w',
        path: '/reservations',
        title: 'Mes réservations',
      },
      {
        component: ProfilePage,
        disabled: false,
        exact: true,
        icon: 'user-w',
        path: '/profil',
        title: 'Mon compte',
      },
      {
        disabled: false,
        exact: true,
        href: 'https://docs.passculture.app/experimentateurs',
        icon: 'help-w',
        target: '_blank',
        title: 'Aide',
      },
      {
        disabled: false,
        exact: true,
        href:
          'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture',
        icon: 'txt-w',
        target: '_blank',
        title: 'Mentions légales',
      },
    ]

    // then
    expect(result).toStrictEqual(expected)
  })
})
