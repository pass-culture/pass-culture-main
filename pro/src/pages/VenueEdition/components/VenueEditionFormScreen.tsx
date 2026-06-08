import { useLocation } from 'react-router'

import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

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
          <Banner
            title="Page invisible"
            description="Publiez une offre pour rendre votre page accessible aux jeunes dans l'application."
            variant={BannerVariants.WARNING}
          />
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
