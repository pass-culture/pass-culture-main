import cn from 'classnames'
import { useId } from 'react'

import type { TopOffersResponseData } from '@/apiClient/v1'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './MostViewedOffers.module.scss'

export interface MostViewedOffersProps {
  topOffers: TopOffersResponseData[]
}

export const MostViewedOffers = ({ topOffers }: MostViewedOffersProps) => {
  const titleId = useId()

  return (
    <section className={styles.container} aria-labelledby={titleId}>
      <h3 id={titleId} className={styles.title}>
        Top offres
      </h3>
      <ol className={styles.list}>
        {topOffers.map((topOffer) => (
          <li key={topOffer.offerId} className={styles.item}>
            <div
              className={cn(styles.thumbnail, {
                [styles['thumbnail-placeholder']]: !topOffer.image?.url,
              })}
            >
              {topOffer.image?.url ? (
                <img
                  src={topOffer.image.url}
                  alt=""
                  aria-hidden="true"
                  loading="lazy"
                />
              ) : (
                <SvgIcon
                  src={strokeOfferIcon}
                  alt=""
                  className={styles['thumbnail-icon']}
                />
              )}
            </div>
            <div className={styles.details}>
              {!topOffer.isHeadlineOffer && (
                <Tag label="À la une" variant={TagVariant.HEADLINE} />
              )}
              <span className={styles.name}>{topOffer.offerName}</span>
              <span className={styles.views}>
                {topOffer.numberOfViews.toLocaleString('fr-FR')}{' '}
                {pluralizeFr(topOffer.numberOfViews, 'vue', 'vues')}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
