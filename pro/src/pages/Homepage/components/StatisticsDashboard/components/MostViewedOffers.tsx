import cn from 'classnames'

import { TopOffersResponseData } from 'apiClient/v1'
import { pluralizeString } from 'commons/utils/pluralize'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import { Thumb } from 'ui-kit/Thumb/Thumb'

import styles from './MostViewedOffers.module.scss'

export interface MostViewedOffersProps {
  last30daysViews: number
  topOffers: TopOffersResponseData[]
}

export const MostViewedOffers = ({
  last30daysViews,
  topOffers,
}: MostViewedOffersProps) => {
  return (
    <div className={styles['container']}>
      <div>
        <h3 className={styles['block-title']}>
          Vos offres ont été vues
          <br />
          {last30daysViews.toLocaleString('fr-FR')} fois
        </h3>
        <span>ces 30 derniers jours</span>
      </div>

      <div className={styles['caption']}>Offres les plus consultées</div>

      <ol className={styles['top-offers']}>
        {topOffers.map((topOffer, index) => (
          <li key={topOffer.offerId} className={styles['top-offer']}>
            <div className={styles['top-offer-rank']}>#{index + 1}</div>
            <Thumb
              url={topOffer.image?.url}
              className={cn(styles['top-offer-thumbnail'], {
                [styles['top-offer-thumbnail-placeholder']]:
                  !topOffer.image?.url,
              })}
            />
            <div className={styles['top-offer-details']}>
              {topOffer.isHeadlineOffer && (
                <div className={styles['top-offer-headline-tag']}>
                  <Tag label="Offre à la une" variant={TagVariant.HEADLINE} />
                </div>
              )}
              <span className={styles['top-offer-title']}>
                {topOffer.offerName}
              </span>
              <br /> {topOffer.numberOfViews.toLocaleString('fr-FR')}{' '}
              {pluralizeString('vue', topOffer.numberOfViews)}
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
