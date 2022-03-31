import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { Audience } from 'core/Offers/types'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import styles from './OfferListFilterTabs.module.scss'

interface IOfferListFilterTabsProps {
  selectedAudience: Audience
}

const OfferListFilterTabs = ({
  selectedAudience,
}: IOfferListFilterTabsProps): JSX.Element => {
  return (
    <div className={styles['offer-list-filter-tabs']}>
      <Link
        className={cn(styles['offer-list-filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.INDIVIDUAL,
        })}
        to="/offres"
      >
        <UserIcon className={styles['offer-list-filter-tabs-tab-icon']} />
        <span>Offres individuelles</span>
      </Link>
      <Link
        className={cn(styles['offer-list-filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.COLLECTIVE,
        })}
        to="/offres/collectives"
      >
        <LibraryIcon className={styles['offer-list-filter-tabs-tab-icon']} />
        <span>Offres collectives</span>
      </Link>
    </div>
  )
}

export default OfferListFilterTabs
