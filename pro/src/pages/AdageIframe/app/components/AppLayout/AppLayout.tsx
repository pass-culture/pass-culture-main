import { Navigate, Route, Routes, useLocation } from 'react-router-dom'

import { AdageFrontRoles, VenueResponse } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'

import useAdageUser from '../../hooks/useAdageUser'
import { AdageDiscovery } from '../AdageDiscovery/AdageDiscovery'
import { AdageHeader } from '../AdageHeader/AdageHeader'
import { OfferInfos } from '../OfferInfos/OfferInfos'
import { OffersFavorites } from '../OffersFavorites/OffersFavorites'
import OffersForMyInstitution from '../OffersForInstitution/OffersForMyInstitution'
import { OffersInstantSearch } from '../OffersInstantSearch/OffersInstantSearch'

import styles from './AppLayout.module.scss'

export const AppLayout = ({
  venueFilter,
}: {
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { adageUser } = useAdageUser()
  const { pathname, search } = useLocation()
  const params = new URLSearchParams(search)

  const isDiscoveryPage = pathname === '/adage-iframe/decouverte'
  const isDiscoveryActive = useActiveFeature('WIP_ENABLE_DISCOVERY')
  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')
  const isUserInMarseilleProgram = (adageUser.programs ?? []).some(
    (prog) => prog.name === 'marseille_en_grand'
  )
  const recirectToMarseilleSearch =
    isMarseilleEnabled && isUserInMarseilleProgram
  const venueId = params.get('venue')

  const redirectToSearch =
    !isDiscoveryActive ||
    venueId ||
    recirectToMarseilleSearch ||
    adageUser.role === AdageFrontRoles.READONLY

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
              redirectToSearch ? (
                <Navigate
                  to={`recherche${search}${
                    //  To apply marseille student level filters only when redirecting to search from '/'
                    recirectToMarseilleSearch ? '&program=marseille' : ''
                  }`}
                />
              ) : (
                <Navigate to={`decouverte${search}`} />
              )
            }
          />
          <Route path="decouverte" element={<AdageDiscovery />} />
          <Route
            path="recherche"
            element={<OffersInstantSearch venueFilter={venueFilter} />}
          />
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
