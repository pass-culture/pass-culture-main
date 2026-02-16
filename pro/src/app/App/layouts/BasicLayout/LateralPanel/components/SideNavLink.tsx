import classnames from 'classnames'
import { NavLink, type To } from 'react-router'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setOpenSection } from '@/commons/store/nav/reducer'
import { openSection } from '@/commons/store/nav/selector'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import type { NavItem } from './SideNavLinks'
import styles from './SideNavLinks.module.scss'
import { SideNavToggleButton } from './SideNavToggleButton'

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
      {icon && (
        <SvgIcon
          src={icon}
          width={NAV_ITEM_ICON_SIZE}
          className={styles.icon}
        />
      )}
      <span
        className={classnames({
          [styles['nav-links-item-title']]: icon,
          [styles['nav-links-item-without-icon']]: !icon,
        })}
      >
        {children}
      </span>
    </NavLink>
  )
}

export const RenderNavItem = ({ item }: { item: NavItem }) => {
  const navOpenSection = useAppSelector(openSection)

  const isExpanded = navOpenSection[item.key as keyof typeof navOpenSection]

  const dispatch = useAppDispatch()

  switch (item.type) {
    case 'link':
      return (
        <li>
          <SideNavLink to={item.to} icon={item.icon}>
            {item.title}
          </SideNavLink>
        </li>
      )

    case 'section':
      return (
        <li>
          <SideNavToggleButton
            icon={item.icon}
            title={item.title}
            isExpanded={isExpanded}
            onClick={() => {
              dispatch(
                setOpenSection({
                  ...navOpenSection,
                  [item.key]: !isExpanded,
                })
              )
            }}
            ariaControls={`${item.key}-sublist`}
            id={`${item.key}-sublist-button`}
          />

          {isExpanded && (
            <ul>
              {item.children.map((children: NavItem) => (
                <RenderNavItem key={`${item.title}`} item={children} />
              ))}
            </ul>
          )}
        </li>
      )
  }
}
