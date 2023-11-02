import cn from 'classnames'
import React from 'react'

import { OffererViewsModel, TopOffersResponseData } from 'apiClient/v1'
import { Thumb } from 'ui-kit'

import styles from './MostViewedOffers.module.scss'

export interface MostViewedOffersProps {
  topOffers: TopOffersResponseData[]
  dailyViews: OffererViewsModel[]
}

export const MostViewedOffers = ({
  topOffers,
  dailyViews,
}: MostViewedOffersProps) => {
  const viewsToday = dailyViews[dailyViews.length - 1].numberOfViews
  const last30daysViews =
    dailyViews.length >= 30
      ? viewsToday - dailyViews[dailyViews.length - 30].numberOfViews
      : viewsToday

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
              <span className={styles['offer-title']}>
                {topOffer.offerName}
              </span>
              <br /> {topOffer.numberOfViews.toLocaleString('fr-FR')} vues
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
