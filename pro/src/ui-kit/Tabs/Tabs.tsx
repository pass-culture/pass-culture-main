import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'
import { Link } from 'react-router-dom'

import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './Tabs.module.scss'

interface ITab {
  label: string
  key: string
  url?: string
  onClick?: () => void
  Icon?: FunctionComponent<SVGProps<SVGSVGElement>>
}
export interface IFilterTabsProps {
  tabs: ITab[]
  selectedKey?: string
}

const Tabs = ({ selectedKey, tabs }: IFilterTabsProps): JSX.Element => {
  return (
    <ul className={styles['tabs']}>
      {tabs.map(({ key, label, url, Icon, onClick }) => {
        return (
          <li
            className={cn(styles['tabs-tab'], {
              [styles['is-selected']]: selectedKey === key,
            })}
            key={`tab_${key}`}
          >
            {url ? (
              <Link
                className={styles['tabs-tab-link']}
                key={`tab${url}`}
                to={url}
              >
                {Icon && <Icon className={styles['tabs-tab-icon']} />}
                <span>{label}</span>
              </Link>
            ) : (
              <Button
                variant={ButtonVariant.TERNARY}
                Icon={Icon}
                onClick={onClick}
                className={styles['tabs-tab-button']}
              >
                {label}
              </Button>
            )}
          </li>
        )
      })}
    </ul>
  )
}

export default Tabs
