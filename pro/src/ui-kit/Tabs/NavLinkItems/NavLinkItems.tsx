import cn from 'classnames'
import { Link } from 'react-router'

import type { BaseTabsProps } from '../Tabs'
import styles from '../Tabs.module.scss'

export type NavLinkItem<T extends string> = {
  /**
   * The label of the nav link.
   */
  label: React.ReactNode
  /**
   * The unique key identifying the nav link.
   */
  key: T
  /**
   * The URL for the navigation link.
   */
  url: string
}

type NavLinkItemsProps<T extends string> = BaseTabsProps<T> & {
  links: NavLinkItem<T>[]
}

export const NavLinkItems = <T extends string>({
  navLabel,
  selectedKey,
  links,
  className,
}: NavLinkItemsProps<T>): JSX.Element => {
  return (
    <nav aria-label={navLabel}>
      {/** biome-ignore lint/correctness/useUniqueElementIds: This is always
          rendered once per page, so there cannot be id duplications.> */}
      <ul id="tablist" className={cn(styles['menu-list'], className)}>
        {links.map(({ key, label, url }) => {
          const isSelected = selectedKey === key

          return (
            <li {...(isSelected ? { id: 'selected' } : {})} key={key}>
              <Link
                to={url}
                className={cn(styles['menu-list-item'], {
                  [styles['is-selected']]: isSelected,
                })}
              >
                <span className={styles['menu-list-item-label']}>
                  {isSelected && (
                    <span className={styles['visually-hidden']}>
                      Lien actif
                    </span>
                  )}
                  {label}
                </span>
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
