import classnames from 'classnames'
import { NavLink, type To } from 'react-router'
import index from 'swr'

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

export const RenderNavItem = ({
  item,
  level = 0,
}: {
  item: NavItem
  level?: number
}) => {
  const navOpenSection = useAppSelector(openSection)

  const hasChildren = item.children && item.children.length > 0
  const isExpanded = navOpenSection[item.key as keyof typeof navOpenSection]
  const dispatch = useAppDispatch()

  if (!hasChildren) {
    if (item.type === 'section') {
      return null
    }

    if (item.type === 'custom') {
      return <li key={index}>{item.component}</li>
    }

    return (
      <li>
        <SideNavLink to={item.to} icon={item.icon}>
          {item.title}
        </SideNavLink>
      </li>
    )
  }

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
          {item.children.map((child: unknown, index: any) => (
            <RenderNavItem
              key={`${item.title}-${index}`}
              item={child}
              level={level + 1}
            />
          ))}
        </ul>
      )}
    </li>
  )
}
