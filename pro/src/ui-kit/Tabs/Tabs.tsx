import cn from 'classnames'
import { useEffect, useRef } from 'react'

import { claimNavigationFocus } from '@/app/App/hook/useFocus'

import styles from './Tabs.module.scss'

export type TabItem<T extends string> = {
  /**
   * The label of the tab.
   */
  label: React.ReactNode
  /**
   * The unique key identifying the tab.
   * This is used to identify the selected tab.
   */
  key: T
  /**
   * Optional URL for navigation. If provided, the caller should handle
   * navigation in the onClick callback using useNavigate or similar router hook.
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

type BaseTabsProps<T extends string> = {
  /**
   * Navigation accessible name
   */
  navLabel: string
  /**
   * The key of the selected link.
   */
  selectedKey?: T
  className?: string
}

type TabsProps<T extends string> = BaseTabsProps<T> & {
  /**
   * An array of tabs to be rendered.
   * Each tab can optionally include a URL for navigation.
   * If a URL is provided, it's stored in the tab data for reference.
   * The onClick handler is responsible for navigation if needed.
   */
  items: TabItem<T>[]
  /**
   * The function called when a tab is clicked or selected
   */
  onClick?: (selectedKey: T) => void
}

export const getTabId = (baseId: string): string => `tab-${baseId}`
export const getPanelId = (baseId: string): string => `panel-${baseId}`

/**
 * The Tabs component is used to render tabs following ARIA best practices.
 * It supports both navigation links and interactive buttons:
 *  - If a tab has a `url` property, the caller should handle navigation in onClick
 *  - If a tab has no `url`, it's purely for handling onClick events
 *
 * @example
 * // With navigation - caller handles navigation
 * const navigate = useNavigate()
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
 *   onClick={(key) => navigate(tabs.find(t => t.key === key)?.url ?? '/')}
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
  const tabRefs = useRef<Record<string, HTMLButtonElement | null>>({})
  const selectedButtonRef = useRef<HTMLButtonElement>(null)

  // Moves focus to the selected tab whenever it (re)appears, e.g. once its
  // data has finished loading, so screen reader users land on it after
  // navigating to the next/previous step.
  useEffect(() => {
    claimNavigationFocus(
      selectedButtonRef.current ?? tabRefs.current[selectedKey ?? '']
    )
  }, [selectedKey])

  const focusTab = (key: T) => {
    tabRefs.current[key]?.focus()
  }

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLButtonElement>,
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
    const newTab = tabs[newIndex]
    focusTab(newTab.key)
    onClick?.(newTab.key)
  }

  return (
    <div>
      <div
        role="tablist"
        aria-label={navLabel}
        className={cn(styles['menu-list'], className)}
      >
        {tabs.map(({ key, label, baseId }, index) => {
          const isSelected = selectedKey === key
          const tabBaseId = baseId ?? key

          return (
            <button
              id={getTabId(tabBaseId)}
              key={key}
              ref={(el) => {
                tabRefs.current[key] = el
                if (isSelected) {
                  selectedButtonRef.current = el
                }
              }}
              type="button"
              role="tab"
              onClick={() => onClick?.(key)}
              onKeyDown={(event) => handleKeyDown(event, index)}
              aria-selected={isSelected}
              aria-controls={getPanelId(tabBaseId)}
              tabIndex={isSelected ? 0 : -1}
              className={cn(
                styles['menu-list-item'],
                styles['menu-list-item-button'],
                {
                  [styles['is-selected']]: isSelected,
                }
              )}
            >
              <span>
                {isSelected && (
                  <span className={styles['visually-hidden']}>
                    Onglet actif
                  </span>
                )}
                <span>{label}</span>
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
