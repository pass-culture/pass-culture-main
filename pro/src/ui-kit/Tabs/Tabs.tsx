import * as TabsPrimitive from '@radix-ui/react-tabs'
import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './Tabs.module.scss'

export interface Tab {
  label: string | React.ReactNode
  key: string
  url?: string
  icon?: string
  /**
   * A flag to display a "new" tag next to the tab.
   */
  isNew?: boolean
}

interface TabsProps {
  nav?: string
  tabs: Tab[]
  selectedKey?: string
  className?: string
}

const NAV_ITEM_ICON_SIZE = '24'

export const Tabs = ({
  nav,
  selectedKey,
  tabs,
  className,
}: TabsProps): JSX.Element => {
  const content = (
    <TabsPrimitive.Root
      className={cn(styles['tabs-root'], className)}
      value={selectedKey}
    >
      <TabsPrimitive.List className={styles['tabs']}>
        {tabs.map(({ key, label, url, icon, isNew = false }) => (
          <TabsPrimitive.Trigger
            className={cn(styles['tabs-tab'], {
              [styles['is-selected']]: selectedKey === key,
            })}
            key={key}
            value={key}
            asChild
          >
            <Link to={url ?? '#'} className={styles['tabs-tab-link']}>
              {icon && (
                <SvgIcon
                  src={icon}
                  alt=""
                  className={styles['tabs-tab-icon']}
                  width={NAV_ITEM_ICON_SIZE}
                />
              )}
              <span className={styles['tabs-tab-label']}>{label}</span>
              {isNew && (
                <Tag
                  className={styles['tabs-tab-new']}
                  variant={TagVariant.BLUE}
                >
                  Nouveau
                </Tag>
              )}
            </Link>
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>
    </TabsPrimitive.Root>
  )

  return nav ? <nav aria-label={nav}>{content}</nav> : content
}
