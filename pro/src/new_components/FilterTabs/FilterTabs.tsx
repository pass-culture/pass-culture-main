import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { Audience } from 'core/Offers/types'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import styles from './FilterTabs.module.scss'

interface IFilterTabsProps {
  selectedAudience: Audience
  individualLink: string
  collectiveLink: string
  individualLabel: string
  collectiveLabel: string
}

const FilterTabs = ({
  selectedAudience,
  individualLink,
  collectiveLink,
  individualLabel,
  collectiveLabel,
}: IFilterTabsProps): JSX.Element => {
  return (
    <div className={styles['filter-tabs']}>
      <Link
        className={cn(styles['filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.INDIVIDUAL,
        })}
        to={individualLink}
      >
        <UserIcon className={styles['filter-tabs-tab-icon']} />
        <span>{individualLabel}</span>
      </Link>
      <Link
        className={cn(styles['filter-tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.COLLECTIVE,
        })}
        to={collectiveLink}
      >
        <LibraryIcon className={styles['filter-tabs-tab-icon']} />
        <span>{collectiveLabel}</span>
      </Link>
    </div>
  )
}

export default FilterTabs
