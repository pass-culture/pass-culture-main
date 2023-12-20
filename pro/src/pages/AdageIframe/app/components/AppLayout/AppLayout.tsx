import { Navigate, Route, Routes, useLocation } from 'react-router-dom'

import { AdageFrontRoles } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'

import useAdageUser from '../../hooks/useAdageUser'
import { AdageDiscovery } from '../AdageDiscovery/AdageDiscovery'
import { AdageHeader } from '../AdageHeader/AdageHeader'
import { OfferInfos } from '../OfferInfos/OfferInfos'
import { OffersFavorites } from '../OffersFavorites/OffersFavorites'
import OffersForMyInstitution from '../OffersForInstitution/OffersForMyInstitution'
import { OffersInstantSearch } from '../OffersInstantSearch/OffersInstantSearch'

import styles from './AppLayout.module.scss'

export const AppLayout = (): JSX.Element => {
  const { adageUser } = useAdageUser()
  const { pathname, search } = useLocation()
  const params = new URLSearchParams(search)

  const isDiscoveryPage = pathname === '/adage-iframe'
  const isDiscoveryActive = useActiveFeature('WIP_ENABLE_DISCOVERY')
  const venueId = Number(params.get('venue'))

  return (
    <div>
      <AdageHeader />
      <main
        className={isDiscoveryPage ? '' : styles['app-layout-content']}
        id="content"
      >
        <Routes>
          <Route
            path=""
            element={
              adageUser.role === AdageFrontRoles.REDACTOR &&
              isDiscoveryActive &&
              !venueId ? (
                <AdageDiscovery />
              ) : (
                <Navigate to={`recherche${search}`} />
              )
            }
          />
          <Route path="recherche" element={<OffersInstantSearch />} />
          <Route
            path="mon-etablissement"
            element={<OffersForMyInstitution />}
          />
          <Route path="mes-favoris" element={<OffersFavorites />} />
          <Route path="decouverte/offre/:offerId" element={<OfferInfos />} />
        </Routes>
      </main>
    </div>
  )
}
