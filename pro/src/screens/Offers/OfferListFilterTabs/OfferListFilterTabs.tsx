import cn from 'classnames'
import React from 'react'

import { Audience } from 'core/Offers/types'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import styles from './OfferListFilterTabs.module.scss'

interface IOfferListFilterTabsProps {
  selectedAudience: Audience
  onSelectAudience: (audience: Audience) => void
}

const OfferListFilterTabs = ({
  selectedAudience,
  onSelectAudience,
}: IOfferListFilterTabsProps): JSX.Element => {
  return (
    <div className={styles['offer-list-filter-tabs']}>
      <label
        className={cn(styles['offer-list-filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.INDIVIDUAL,
        })}
      >
        <UserIcon className={styles['offer-list-filter-tabs-tab-icon']} />
        <input
          checked={selectedAudience === Audience.INDIVIDUAL}
          className={styles['offer-list-filter-tabs-tab-radio']}
          name="audience"
          onChange={() => onSelectAudience(Audience.INDIVIDUAL)}
          type="radio"
          value="individual"
        />
        Offres individuelles
      </label>
      <label
        className={cn(styles['offer-list-filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.COLLECTIVE,
        })}
      >
        <LibraryIcon className={styles['offer-list-filter-tabs-tab-icon']} />
        <input
          checked={selectedAudience === Audience.COLLECTIVE}
          className={styles['offer-list-filter-tabs-tab-radio']}
          name="audience"
          onChange={() => onSelectAudience(Audience.COLLECTIVE)}
          type="radio"
          value="collective"
        />
        Offres collectives
      </label>
    </div>
  )
}

export default OfferListFilterTabs
