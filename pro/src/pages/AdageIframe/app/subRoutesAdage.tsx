/* No need to test this file */
/* istanbul ignore file */
import OffersForMyInstitution from './components/OffersForInstitution/OffersForMyInstitution'
import { OffersInstantSearch } from './components/OffersInstantSearch/OffersInstantSearch'

export const routesAdage = [
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
]

export default routesAdage
