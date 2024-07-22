import cn from 'classnames'
import React from 'react'

import { TopOffersResponseData } from 'apiClient/v1'
import { Thumb } from 'ui-kit/Thumb/Thumb'
import { pluralizeString } from 'utils/pluralize'

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
                [styles['top-offer-thumbnail-placeholder'] ?? '']:
                  !topOffer.image?.url,
              })}
            />
            <div className={styles['top-offer-details']}>
              <span className={styles['offer-title']}>
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
