import cn from 'classnames'

import type { BaseTabsProps } from '../Tabs'
import styles from '../Tabs.module.scss'

export type TabItem = {
  /**
   * The label of the tab.
   */
  label: React.ReactNode
  /**
   * The unique key identifying the tab.
   * This is used to identify the selected tab.
   */
  key: string
  /**
   * The corresponding tab element's id
   * It should be used in the `aria-labelledby` attribute
   *  of the corresponding panel element.
   * @default `tab-${key}`
   */
  tabId?: string
  /**
   * The corresponding tab element's id
   * It's used in the `aria-controls` attribute
   *   of the corresponding tab element
   * @default `panel-${key}`
   */
  panelId?: string
}

type TabItemsProps = BaseTabsProps & {
  navLabel: string
  tabs: TabItem[]
  onChange: (selectedKey: string) => void
}

export const TabItems = ({
  navLabel,
  tabs,
  onChange,
  selectedKey,
  className,
}: TabItemsProps): JSX.Element => {
  return (
    <div>
      <div
        role="tablist"
        aria-label={navLabel}
        className={cn(styles['menu-list'], className)}
      >
        {tabs.map(({ key, label, tabId, panelId }) => {
          const isSelected = selectedKey === key

          return (
            /**
             * We use a button tag to follow ARIA best practices for tab role
             * @see https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/tab_role#best_practices
             */
            <button
              id={tabId ?? `tab-${key}`}
              key={key}
              type="button"
              role="tab"
              onClick={() => onChange(key)}
              aria-selected={isSelected}
              aria-controls={panelId ?? `panel-${key}`}
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
              <span className={styles['menu-list-item-label']}>
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
