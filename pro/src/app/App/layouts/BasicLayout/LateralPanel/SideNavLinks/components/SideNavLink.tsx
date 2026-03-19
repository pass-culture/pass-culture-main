import classnames from 'classnames'
import { useState } from 'react'
import { NavLink, type To } from 'react-router'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import type { NavItem } from '../SideNavLinks'
import styles from './SideNavLink.module.scss'
import { SideNavToggleButton } from './SideNavToggleButton'

const NAV_ITEM_ICON_SIZE = '20'

interface SideNavLinkProps {
  to: To
  children: React.ReactNode
  icon?: string
  end?: boolean
  showNotification?: boolean
}

const SideNavLink = ({
  to,
  children,
  icon,
  end = false,
  showNotification = false,
}: SideNavLinkProps) => {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        classnames(styles['nav-links-item'], {
          [styles['nav-links-item-active']]: isActive,
        })
      }
    >
      {icon && <SvgIcon src={icon} width={NAV_ITEM_ICON_SIZE} />}
      <span
        className={classnames({
          [styles['nav-links-item-without-icon']]: !icon,
        })}
      >
        {children}
        {showNotification && (
          <span
            className={styles['nav-links-item-notification']}
            aria-hidden="true"
          />
        )}
      </span>
    </NavLink>
  )
}

export const RenderNavItem = ({ item }: { item: NavItem }) => {
  const [open, setOpen] = useState(true)

  switch (item.type) {
    case 'link':
      return (
        <li>
          {item.to && (
            <SideNavLink
              to={item.to}
              icon={item.icon}
              end={item.end}
              showNotification={item.showNotification}
            >
              {item.title}
            </SideNavLink>
          )}
        </li>
      )

    case 'section':
      return (
        <li>
          <SideNavToggleButton
            icon={item.icon || ''}
            title={item.title || ''}
            isExpanded={open}
            onClick={() => setOpen(!open)}
            ariaControls={`${item.key}-sublist`}
            id={`${item.key}-sublist-button`}
          />

          {open && (
            <ul id={`${item.key}-sublist`}>
              {item.children?.map((children: NavItem) => (
                <RenderNavItem key={`${children.key}`} item={children} />
              ))}
            </ul>
          )}
        </li>
      )
    default:
      return null
  }
}
