import React from 'react'

import Icon from 'components/layout/Icon'

import styles from './NoOffers.module.scss'

const NoOffers = (): JSX.Element => {
  return (
    <div className={styles['no-search-results']}>
      <Icon className={styles['no-search-results-icon']} svg="ticket-cross" />
      <p>Vous n’avez pas encore créé d’offre.</p>
    </div>
  )
}

export default NoOffers
