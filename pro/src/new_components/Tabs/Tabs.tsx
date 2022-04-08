import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { Audience } from 'core/shared/types'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import styles from './Tabs.module.scss'

interface ITabsProps {
  selectedAudience: Audience
  individualLink: string
  collectiveLink: string
  individualLabel: string
  collectiveLabel: string
}

const Tabs = ({
  selectedAudience,
  individualLink,
  collectiveLink,
  individualLabel,
  collectiveLabel,
}: ITabsProps): JSX.Element => {
  return (
    <ul className={styles['tabs']}>
      <li
        className={cn(styles['tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.INDIVIDUAL,
        })}
      >
        <Link className={styles['tabs-tab-link']} to={individualLink}>
          <UserIcon className={styles['tabs-tab-icon']} />
          <span>{individualLabel}</span>
        </Link>
      </li>
      <li
        className={cn(styles['tabs-tab'], {
          [styles['is-selected']]: selectedAudience === Audience.COLLECTIVE,
        })}
      >
        <Link className={styles['tabs-tab-link']} to={collectiveLink}>
          <LibraryIcon className={styles['tabs-tab-icon']} />
          <span>{collectiveLabel}</span>
        </Link>
      </li>
    </ul>
  )
}

export default Tabs
