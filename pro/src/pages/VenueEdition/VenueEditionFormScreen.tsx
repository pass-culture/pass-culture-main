import { useLocation } from 'react-router'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import { VenueEditionForm } from './VenueEditionForm'
import styles from './VenueEditionFormScreen.module.scss'
import { VenueEditionReadOnly } from './VenueEditionReadOnly'

interface VenueEditionProps {
  venue: GetVenueResponseModel
}

export const VenueEditionFormScreen = ({
  venue,
}: VenueEditionProps): JSX.Element => {
  const shouldDisplayAccessToPageWarning =
    venue.isPermanent && venue.hasOffers && !venue.hasActiveIndividualOffer

  const location = useLocation()

  return (
    <>
      {shouldDisplayAccessToPageWarning && (
        <div className={styles['page-status']}>
          <Callout variant={CalloutVariant.WARNING}>
            Sans offre publiée, les jeunes n’ont pas accès à votre page sur
            l’application.
          </Callout>
        </div>
      )}

      {location.pathname.includes('/edition') ? (
        <VenueEditionForm venue={venue} />
      ) : (
        <VenueEditionReadOnly venue={venue} />
      )}
    </>
  )
}
