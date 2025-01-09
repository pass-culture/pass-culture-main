import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { UNAVAILABLE_ERROR_PAGE } from 'commons/utils/routes'
import {
  getPhysicalVenuesFromOfferer,
  getVirtualVenueFromOfferer,
} from 'pages/Homepage/components/Offerers/components/VenueList/venueUtils'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { DialogNoVenue } from '../DialogNoVenue/DialogNoVenue'
import dialogNoVenueStyles from '../DialogNoVenue/DialogNoVenue.module.scss'

import styles from './VenueCreationLinks.module.scss'

interface VenueCreationLinksProps {
  offerer?: GetOffererResponseModel | null
}

export const VenueCreationLinks = ({ offerer }: VenueCreationLinksProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const virtualVenue = getVirtualVenueFromOfferer(offerer)
  const physicalVenues = getPhysicalVenuesFromOfferer(offerer)
  const hasVirtualOffers = Boolean(virtualVenue)
  const hasPhysicalVenue = physicalVenues.length > 0

  if (!hasPhysicalVenue) {
    return
  }

  const venueCreationUrl = isVenueCreationAvailable
    ? `/parcours-inscription/structure`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <div className={styles['container']}>
      <div className={styles['add-venue-button']}>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          to={venueCreationUrl}
          onClick={() => {
            logEvent(Events.CLICKED_CREATE_VENUE, {
              from: location.pathname,
              is_first_venue: !hasVirtualOffers,
            })
          }}
        >
          {isOfferAddressEnabled ? 'Ajouter une structure' : 'Ajouter un lieu'}
        </ButtonLink>
      </div>
      {isOfferAddressEnabled && (
        <div className={styles['add-venue-button']}>
          <DialogBuilder
            className={dialogNoVenueStyles['dialog']}
            trigger={
              <Button variant={ButtonVariant.SECONDARY}>Ajouter un lieu</Button>
            }
          >
            <DialogNoVenue />
          </DialogBuilder>
        </div>
      )}
    </div>
  )
}
