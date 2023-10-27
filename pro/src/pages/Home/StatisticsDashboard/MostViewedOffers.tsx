import cn from 'classnames'
import React from 'react'

import { OffererViewsModel, TopOffersResponseData } from 'apiClient/v1'
import { Thumb } from 'ui-kit'

import styles from './MostViewedOffers.module.scss'

interface MostViewedOffersProps {
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
          Vos offres ont été vues {last30daysViews} fois
        </h3>
        <span>ces 30 derniers jours</span>
      </div>

      <div className={styles['caption']}>Offres les plus consultées</div>

      {topOffers.map((topOffer, index) => (
        <div key={topOffer.offerId} className={styles['top-offer']}>
          <div className={styles['top-offer-rank']}>#{index + 1}</div>
          <Thumb
            url={topOffer.image?.url}
            className={cn(styles['top-offer-thumbnail'], {
              [styles['top-offer-thumbnail-placeholder']]: !topOffer.image?.url,
            })}
          />
          <div className={styles['top-offer-details']}>
            {topOffer.offerName}
            <br /> {topOffer.numberOfViews} vues
          </div>
        </div>
      ))}
    </div>
  )
}
