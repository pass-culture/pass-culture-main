import cn from 'classnames'
import { useEffect, useRef } from 'react'

import { claimNavigationFocus } from '@/app/App/hook/useFocus'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  type ButtonIconColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'

import styles from './Tabs.module.scss'

type TabElement = HTMLButtonElement | HTMLAnchorElement

export type TabItem<T extends string> = {
  /**
   * The label of the tab.
   */
  label: string
  /**
   * Optional icon displayed after the label.
   */
  icon?: string
  /**
   * Alternative text of the icon.
   */
  iconAlt?: string
  /**
   * The color of the icon, when it must differ from the label color.
   */
  iconColor?: ButtonIconColor
  /**
   * The unique key identifying the tab.
   * This is used to identify the selected tab.
   */
  key: T
  /**
   * Optional URL for navigation. If provided, the tab is rendered as a
   * router link and navigation is handled natively, without needing `onClick`.
   */
  url?: string
  /**
   * Base string used to derive DOM ids for tab and panel elements.
   *
   * The generated ids are computed according to the following convention :
   *
   * 1. Tab element id: `tab-${baseId}`
   *    It should be used in the `aria-labelledby` attribute
   *    of the corresponding panel element.
   *
   * 2. Panel element id: `panel-${baseId}`:
   *    Used in the `aria-controls` attribute of the tab element.
   *    It should be used as the id of the corresponding panel.
   *
   * Defaults to the value of `key`.
   */
  baseId?: string
}

type TabsProps<T extends string> = {
  /**
   * Navigation accessible name
   */
  navLabel: string
  /**
   * The key of the selected link.
   */
  selectedKey?: T
  className?: string
  /**
   * An array of tabs to be rendered.
   * Each tab can optionally include a URL for navigation.
   * If a URL is provided, the tab is rendered as a router link.
   */
  items: TabItem<T>[]
  /**
   * The function called when a tab is clicked or selected.
   * For tabs with a `url`, it is called in addition to the navigation.
   */
  onClick?: (selectedKey: T) => void
}

export const getTabId = (baseId: string): string => `tab-${baseId}`
export const getPanelId = (baseId: string): string => `panel-${baseId}`

/**
 * The Tabs component is used to render tabs following ARIA best practices.
 * It supports both navigation links and interactive buttons:
 *  - If a tab has a `url` property, it is rendered as a router link
 *  - If a tab has no `url`, it's purely for handling onClick events
 *
 * @example
 * // With navigation
 * <Tabs
 *   items={[{
 *     key: 'home',
 *     label: 'Home',
 *     url: '/home',
 *   }, {
 *     key: 'profile',
 *     label: 'Profile',
 *     url: '/profile',
 *   }]}
 *   selectedKey="home"
 *   navLabel="Navigation"
 * />
 *
 * // With buttons (no navigation)
 * <Tabs
 *   items={[{
 *     key: 'details',
 *     label: 'Details',
 *   }, {
 *     key: 'reviews',
 *     label: 'Reviews',
 *   }]}
 *   selectedKey="details"
 *   onClick={(key) => setActiveTab(key)}
 *   navLabel="Content tabs"
 * />
 */
export const Tabs = <T extends string>({
  navLabel,
  items: tabs,
  onClick,
  selectedKey,
  className,
}: TabsProps<T>): JSX.Element => {
  const tabRefs = useRef<Record<string, TabElement | null>>({})
  const selectedTabRef = useRef<TabElement | null>(null)

  // Moves focus to the selected tab whenever it (re)appears, e.g. once its
  // data has finished loading, so screen reader users land on it after
  // navigating to the next/previous step.
  useEffect(() => {
    claimNavigationFocus(
      selectedTabRef.current ?? tabRefs.current[selectedKey ?? '']
    )
  }, [selectedKey])

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLElement>,
    index: number
  ) => {
    let newIndex: number | null = null

    switch (event.key) {
      case 'ArrowRight':
        newIndex = (index + 1) % tabs.length
        break
      case 'ArrowLeft':
        newIndex = (index - 1 + tabs.length) % tabs.length
        break
      case 'Home':
        newIndex = 0
        break
      case 'End':
        newIndex = tabs.length - 1
        break
      default:
        return
    }

    event.preventDefault()
    const newTabElement = tabRefs.current[tabs[newIndex].key]
    newTabElement?.focus()
    // Activates the tab like a click would, so link tabs navigate natively
    newTabElement?.click()
  }

  return (
    <div>
      <div
        role="tablist"
        aria-label={navLabel}
        className={cn(styles['menu-list'], className)}
      >
        {tabs.map(
          ({ key, label, baseId, url, icon, iconAlt, iconColor }, index) => {
            const isSelected = selectedKey === key
            const tabBaseId = baseId ?? key

            const tabProps = {
              id: getTabId(tabBaseId),
              ref: (el: TabElement | null) => {
                tabRefs.current[key] = el
                if (isSelected) {
                  selectedTabRef.current = el
                }
              },
              role: 'tab',
              label,
              icon,
              iconAlt,
              iconColor,
              iconPosition: IconPositionEnum.RIGHT,
              variant: ButtonVariant.TERTIARY,
              color: isSelected ? ButtonColor.BRAND : ButtonColor.NEUTRAL,
              onClick: () => onClick?.(key),
              onKeyDown: (event: React.KeyboardEvent<HTMLElement>) =>
                handleKeyDown(event, index),
              'aria-selected': isSelected,
              'aria-controls': getPanelId(tabBaseId),
              tabIndex: isSelected ? 0 : -1,
            }

            return url ? (
              <Button key={key} as="router-link" to={url} {...tabProps} />
            ) : (
              <Button key={key} as="button" {...tabProps} />
            )
          }
        )}
      </div>
    </div>
  )
}
