import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import { VenueEditionForm } from './VenueEditionForm'
import styles from './VenueEditionFormScreen.module.scss'

interface VenueEditionProps {
  venue: GetVenueResponseModel
}

export const VenueEditionFormScreen = ({
  venue,
}: VenueEditionProps): JSX.Element => {
  const shouldDisplayAccessToPageWarning =
    venue.isPermanent && venue.hasOffers && !venue.hasActiveIndividualOffer

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

      <VenueEditionForm venue={venue} />
    </>
  )
}
