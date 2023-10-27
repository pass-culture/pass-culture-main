import React from 'react'

import styles from './CumulatedViews.module.scss'

export const CumulatedViews = () => {
  return (
    <div className={styles['cumulated-views']}>
      <div>
        <h3 className={styles['block-title']}>
          Évolution des consultations de vos offres
        </h3>
        <span>ces 6 derniers mois</span>
      </div>

      <div>TODO graphique</div>
    </div>
  )
}
