import classnames from 'classnames'
import { NavLink, type To } from 'react-router'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SideNavLinks.module.scss'

const NAV_ITEM_ICON_SIZE = '20'

interface SideNavLinkProps {
  to: To
  children: React.ReactNode
  icon?: string
  end?: boolean
  className?: string
}

export const SideNavLink = ({
  to,
  children,
  icon,
  end = false,
  className,
}: SideNavLinkProps) => {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        classnames(styles['nav-links-item'], className, {
          [styles['nav-links-item-active']]: isActive,
        })
      }
    >
      {icon ? (
        <>
          <SvgIcon
            src={icon}
            alt=""
            width={NAV_ITEM_ICON_SIZE}
            className={styles.icon}
          />
          <span className={styles['nav-links-item-title']}>{children}</span>
        </>
      ) : (
        <span className={styles['nav-links-item-without-icon']}>
          {children}
        </span>
      )}
    </NavLink>
  )
}
