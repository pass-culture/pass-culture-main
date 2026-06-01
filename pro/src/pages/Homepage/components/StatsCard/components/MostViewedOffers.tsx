import cn from 'classnames'

import type { TopOffersResponseData } from '@/apiClient/v1'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from './MostViewedOffers.module.scss'

export interface MostViewedOffersProps {
  topOffers: TopOffersResponseData[]
}

export const MostViewedOffers = ({ topOffers }: MostViewedOffersProps) => {
  return (
    <div className={styles['container']}>
      <div>
        <h3 className={styles['block-title']}>Top offres</h3>
      </div>

      <ol className={styles['top-offers']}>
        {topOffers.map((topOffer) => (
          <li key={topOffer.offerId} className={styles['top-offer']}>
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
              </span>{' '}
              <span className={styles['top-offer-views']}>
                {topOffer.numberOfViews.toLocaleString('fr-FR')}{' '}
                {pluralizeFr(topOffer.numberOfViews, 'vue', 'vues')}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
