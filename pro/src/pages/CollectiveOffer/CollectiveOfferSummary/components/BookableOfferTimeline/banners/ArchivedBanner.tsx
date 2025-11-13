import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import styles from '../BookableOfferTimeline.module.scss'

export const ArchivedBanner = () => {
  return (
    <div className={styles['callout']}>
      <Banner
        title="Informations"
        description="Vous avez archivé cette offre. Elle n'est plus visible sur ADAGE."
        variant={BannerVariants.DEFAULT}
      />
    </div>
  )
}
