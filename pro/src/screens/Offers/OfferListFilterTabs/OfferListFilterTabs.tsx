import cn from 'classnames'
import React from 'react'

import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import styles from './OfferListFilterTabs.module.scss'

interface IOfferListFilterTabsProps {
  selectedAudience: 'individual' | 'collective'
  setSelectedAudience: (audience: 'individual' | 'collective') => void
}

const OfferListFilterTabs = ({
  selectedAudience,
  setSelectedAudience,
}: IOfferListFilterTabsProps): JSX.Element => {
  return (
    <div className={styles['offer-list-filter-tabs']}>
      <label
        className={cn(styles['offer-list-filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === 'individual',
        })}
      >
        <UserIcon className={styles['offer-list-filter-tabs-tab-icon']} />
        <input
          checked={selectedAudience === 'individual'}
          className={styles['offer-list-filter-tabs-tab-radio']}
          name="audience"
          onChange={() => setSelectedAudience('individual')}
          type="radio"
          value="individual"
        />
        Offres individuelles
      </label>
      <label
        className={cn(styles['offer-list-filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === 'collective',
        })}
      >
        <LibraryIcon className={styles['offer-list-filter-tabs-tab-icon']} />
        <input
          checked={selectedAudience === 'collective'}
          className={styles['offer-list-filter-tabs-tab-radio']}
          name="audience"
          onChange={() => setSelectedAudience('collective')}
          type="radio"
          value="collective"
        />
        Offres collectives
      </label>
    </div>
  )
}

export default OfferListFilterTabs
