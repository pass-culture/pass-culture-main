/* No need to test this file */
/* istanbul ignore file */
import { AdageDiscovery } from './components/AdageDiscovery/AdageDiscovery'
import { OffersFavorites } from './components/OffersFavorites/OffersFavorites'
import OffersForMyInstitution from './components/OffersForInstitution/OffersForMyInstitution'
import { OffersInstantSearch } from './components/OffersInstantSearch/OffersInstantSearch'

// TODO: delete when ff WIP_ENABLE_DISCOVERY is deleted
export const oldRoutesAdage = [
  {
    element: OffersInstantSearch,
    parentPath: '/adage-iframe',
    path: '/',
    title: 'Recherche',
  },
  {
    element: OffersForMyInstitution,
    parentPath: '/adage-iframe',
    path: '/mon-etablissement',
    title: 'Pour mon établissement',
  },
  {
    element: OffersFavorites,
    parentPath: '/adage-iframe',
    path: '/mes-favoris',
    title: 'Mes Favoris',
  },
]

export const routesAdage = [
  {
    element: AdageDiscovery,
    parentPath: '/adage-iframe',
    path: '/decouverte',
    title: 'Découvrir',
  },
  {
    element: OffersInstantSearch,
    parentPath: '/adage-iframe',
    path: '/',
    title: 'Recherche',
  },
  {
    element: OffersForMyInstitution,
    parentPath: '/adage-iframe',
    path: '/mon-etablissement',
    title: 'Pour mon établissement',
  },
  {
    element: OffersFavorites,
    parentPath: '/adage-iframe',
    path: '/mes-favoris',
    title: 'Mes Favoris',
  },
]
