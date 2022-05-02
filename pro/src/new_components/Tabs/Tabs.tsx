import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'
import { Link, useLocation } from 'react-router-dom'

import styles from './Tabs.module.scss'

interface ITab {
  label: string
  key: string
  url: string
  Icon?: FunctionComponent<SVGProps<SVGSVGElement>>
}
interface IFilterTabsProps {
  tabs: ITab[]
  selectedKey?: string
  withQueryParams?: boolean
}

const Tabs = ({
  selectedKey,
  tabs,
  withQueryParams,
}: IFilterTabsProps): JSX.Element => {
  const { search } = useLocation()

  return (
    <ul className={styles['tabs']}>
      {tabs.map(({ key, label, url, Icon }) => {
        const to = withQueryParams
          ? `${url}?${new URLSearchParams(search).toString()}`
          : url
        return (
          <li
            className={cn(styles['tabs-tab'], {
              [styles['is-selected']]: selectedKey === key,
            })}
            key={`tab_${url}`}
          >
            <Link className={styles['tabs-tab-link']} key={`tab${url}`} to={to}>
              {Icon && <Icon className={styles['tabs-tab-icon']} />}
              <span>{label}</span>
            </Link>
          </li>
        )
      })}
    </ul>
  )
}

export default Tabs
