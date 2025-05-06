import cn from 'classnames'
import { Link } from 'react-router'

import styles from './NavLinkItems.module.scss'

export type NavLinkItem = {
  /**
   * The label of the nav link.
   */
  label: React.ReactNode
  /**
   * The unique key identifying the nav link.
   */
  key: string
  /**
   * The URL for the navigation link.
   */
  url: string
}

type NavLinkItemsProps = {
  /**
   * Navigation accessible name
   */
  navLabel: string
  /**
   * An array of links to be rendered.
   */
  links: NavLinkItem[]
  /**
   * The key of the selected link.
   */
  selectedKey?: string
  className?: string
}

/**
 * The NavLinkItems component is used to render a list of navigation links.
 *
 * @example
 * <NavLinkItems
 *   links={[{
 *     key: 'home',
 *     label: 'Home',
 *     url: '/home',
 *   }, {
 *     key: 'profile',
 *     label: 'Profile',
 *     url: '/profile',
 *   }]}
 *   selectedKey="home"
 * />
 */
export const NavLinkItems = ({
  navLabel,
  selectedKey,
  links,
  className,
}: NavLinkItemsProps): JSX.Element => {
  return (
    <nav aria-label={navLabel}>
      <ul className={cn(styles['menu-list'], className)}>
        {links.map(({ key, label, url }) => (
          <li key={key}>
            <Link
              to={url}
              className={cn(styles['menu-list-item'], {
                [styles['is-selected']]: selectedKey === key,
              })}
            >
              <span className={styles['menu-list-item-label']}>
                {selectedKey === key && (
                  <span className={styles['visually-hidden']}>Lien actif</span>
                )}
                {label}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}
