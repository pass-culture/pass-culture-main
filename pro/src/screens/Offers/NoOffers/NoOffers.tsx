import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

import styles from './NoOffers.module.scss'

const NoOffers = (): JSX.Element => {
  return (
    <div className={styles['no-search-results']}>
      <Icon
        className={styles['no-search-results-icon']}
        svg="ico-ticket-gray"
      />

      <p className={styles['no-search-results-highlight']}>Aucune offre</p>
      <p>Vous n’avez pas encore créé d’offre.</p>

      <Link
        className={cn(
          styles['no-search-results-link'],
          'primary-button with-icon'
        )}
        to="/offre/creation"
      >
        <AddOfferSvg />
        Créer ma première offre
      </Link>
    </div>
  )
}

export default NoOffers
