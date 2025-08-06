import classNames from 'classnames'
import {
  Navigate,
  Route,
  Routes,
  ScrollRestoration,
  useLocation,
} from 'react-router'

import { AdageFrontRoles } from '@/apiClient/adage'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

import { MARSEILLE_EN_GRAND } from '../../constants'
import { useAdageUser } from '../../hooks/useAdageUser'
import { AdageDiscovery } from '../AdageDiscovery/AdageDiscovery'
import { AdageHeader } from '../AdageHeader/AdageHeader'
import { OfferInfos } from '../OfferInfos/OfferInfos'
import { OffersFavorites } from '../OffersFavorites/OffersFavorites'
import { OffersForMyInstitution } from '../OffersForInstitution/OffersForMyInstitution'
import { OffersInstantSearch } from '../OffersInstantSearch/OffersInstantSearch'
import styles from './AppLayout.module.scss'

export const AppLayout = (): JSX.Element => {
  const { adageUser } = useAdageUser()
  const { pathname, search } = useLocation()
  const params = new URLSearchParams(search)

  const isFullWidthPage =
    pathname === '/adage-iframe/decouverte' || pathname.includes('/offre/')
  const isMarseilleEnabled = useActiveFeature('ENABLE_MARSEILLE')
  const isUserInMarseilleProgram = (adageUser.programs ?? []).some(
    (prog) => prog.name === MARSEILLE_EN_GRAND
  )
  const redirectToMarseilleSearch =
    isMarseilleEnabled && isUserInMarseilleProgram
  const venueId = params.get('venue')
  const offerId = params.get('offerid')
  const tab = params.get('tab')

  const redirectToSearch =
    venueId ||
    redirectToMarseilleSearch ||
    adageUser.role === AdageFrontRoles.READONLY

  const getRedirectPath = (): string => {
    if (offerId) {
      return `decouverte/offre/${offerId}${search}`
    }

    switch (tab) {
      case 'institution':
        return `mon-etablissement${search}`
      case 'favoris':
        return `mes-favoris${search}`
      case 'recherche':
        return `recherche${search}`
      case 'decouverte':
        return `decouverte${search}`
      case null:
      default:
        if (redirectToSearch) {
          return `recherche${search}${
            redirectToMarseilleSearch ? '&program=marseille' : ''
          }`
        }
        return `decouverte${search}`
    }
  }

  return (
    <div className={styles['app-layout']}>
      <AdageHeader />
      <main
        className={classNames({
          [styles['app-layout-content']]: !isFullWidthPage,
        })}
        id="content"
      >
        <ScrollRestoration />
        <Routes>
          <Route path="" element={<Navigate to={getRedirectPath()} />} />
          <Route path="decouverte" element={<AdageDiscovery />} />
          <Route path="recherche" element={<OffersInstantSearch />} />
          <Route
            path="mon-etablissement"
            element={<OffersForMyInstitution />}
          />
          <Route path="mes-favoris" element={<OffersFavorites />} />
          <Route path="decouverte/offre/:offerId" element={<OfferInfos />} />
          <Route path="recherche/offre/:offerId" element={<OfferInfos />} />
          <Route path="mes-favoris/offre/:offerId" element={<OfferInfos />} />
          <Route
            path="mon-etablissement/offre/:offerId"
            element={<OfferInfos />}
          />
        </Routes>
      </main>
    </div>
  )
}
