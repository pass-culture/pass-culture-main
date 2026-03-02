import cn from 'classnames'

import type { BaseTabsProps } from '../Tabs'
import styles from './TabItems.module.scss'

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

type TabItemsProps<T extends string> = BaseTabsProps<T> & {
  navLabel: string
  tabs: TabItem<T>[]
  onChange: (selectedKey: T) => void
}

export const getTabId = (baseId: string): string => `tab-${baseId}`
export const getPanelId = (baseId: string): string => `panel-${baseId}`

export const TabItems = <T extends string>({
  navLabel,
  tabs,
  onChange,
  selectedKey,
  className,
}: TabItemsProps<T>): JSX.Element => {
  return (
    <div>
      <div
        role="tablist"
        aria-label={navLabel}
        className={cn(styles['menu-list'], className)}
      >
        {tabs.map(({ key, label, baseId }) => {
          const isSelected = selectedKey === key

          return (
            /**
             * We use a button tag to follow ARIA best practices for tab role
             * @see https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/tab_role#best_practices
             */
            <button
              id={getTabId(baseId ?? key)}
              key={key}
              type="button"
              role="tab"
              onClick={() => onChange(key)}
              aria-selected={isSelected}
              aria-controls={getPanelId(baseId ?? key)}
              tabIndex={0}
              className={cn(
                styles['menu-list-item'],
                // the syle line below reset default button styling
                // so that it doesn't conflict with 'menu-list-item' style
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
                {label}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
