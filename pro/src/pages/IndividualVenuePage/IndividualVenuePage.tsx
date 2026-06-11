import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import { IndividualVenuePageScreen } from './components/IndividualVenuePageScreen'
import styles from './IndividualVenuePage.module.scss'

export const IndividualVenuePage = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const shouldDisplayAccessToPageWarning =
    selectedPartnerVenue.isPermanent &&
    selectedPartnerVenue.hasOffers &&
    !selectedPartnerVenue.hasActiveIndividualOffer

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

      <IndividualVenuePageScreen />
    </>
  )
}

// Lazy-loaded by react-router
export const Component = IndividualVenuePage
