import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import styles from '../BookableOfferTimeline.module.scss'

export const UnderReviewBanner = () => {
  return (
    <div className={styles['callout']}>
      <Banner
        title="Informations"
        variant={BannerVariants.DEFAULT}
        description="Votre offre est en cours d'instruction par notre équipe chargée du contrôle de conformité. Ce contrôle peut prendre jusqu'à 72 heures. Vous serez notifié par mail lors de sa validation ou de son refus."
      />
    </div>
  )
}
