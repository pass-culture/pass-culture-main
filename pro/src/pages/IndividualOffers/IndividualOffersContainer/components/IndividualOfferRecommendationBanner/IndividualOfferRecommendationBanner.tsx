import { Tag, TagVariant } from '@/design-system/Tag/Tag'

import imgGtmReco from './assets/gtm-reco.png'
import styles from './IndividualOfferRecommendationBanner.module.scss'

export const IndividualOfferRecommendationBanner = () => {
  return (
    <div className={styles['recommendation-banner']}>
      <div className={styles['recommendation-banner-content']}>
        <Tag label="Nouveau" variant={TagVariant.NEW} />
        <p className={styles['recommendation-banner-title']}>
          Ajoutez une recommandation pour faire découvrir votre offre
        </p>
        <p className={styles['recommendation-banner-subtitle']}>
          Pour ce faire, rendez-vous dans la section “Mise en avant” de votre
          offre !
        </p>
      </div>
      <img
        className={styles['recommendation-banner-img']}
        src={imgGtmReco}
        aria-hidden={true}
        alt={''}
      />
    </div>
  )
}
