import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  LAPTOP_MEDIA_QUERY,
  useMediaQuery,
} from '@/commons/hooks/useMediaQuery'
import { setSideNavOpenSection } from '@/commons/store/nav/reducer'
import { sideNavOpenSectionSelector } from '@/commons/store/nav/selectors'

import { HelpDropdownNavItem } from './components/HelpDropdownNavItem'
import { RenderNavItem } from './components/SideNavLink'
import { UserReviewDialog } from './components/UserReviewDialog/UserReviewDialog'
import styles from './SideNavLinks.module.scss'

type NavGroup = 'main' | 'footer'
export interface NavItem {
  key: string
  group: NavGroup
  type: string
  title: string
  icon?: string
  to?: string
  end?: boolean
  children?: NavItem[]
}

interface SideNavLinksProps {
  navItems: NavItem[]
  isAdminSpace?: boolean
}
export const SideNavLinks = ({
  isAdminSpace = false,
  navItems,
}: Readonly<SideNavLinksProps>) => {
  const mainItems = navItems.filter((i) => i.group === 'main')
  const footerItems = navItems.filter((i) => i.group === 'footer')

  const isMobileScreen = useMediaQuery(LAPTOP_MEDIA_QUERY)
  const location = useLocation()
  const dispatch = useAppDispatch()
  const lastOpenSection = useAppSelector(sideNavOpenSectionSelector)

  const sections = mainItems.filter((i) => i.type === 'section')
  const firstSectionKey = sections[0]?.key ?? null

  // BasicLayout remounts on every navigation so we use pathName to keep the right section open,
  // and fall back to the last open section (kept in the store) when no section matches the route
  const sectionMatchingCurrentRoute =
    sections.find((section) =>
      section.children?.some((child) => child.to === location.pathname)
    )?.key ?? null

  const [openSection, setOpenSection] = useState<string | null>(() =>
    isAdminSpace
      ? firstSectionKey
      : (sectionMatchingCurrentRoute ?? lastOpenSection)
  )

  useEffect(() => {
    if (!isAdminSpace && sectionMatchingCurrentRoute) {
      dispatch(setSideNavOpenSection(sectionMatchingCurrentRoute))
    }
  }, [dispatch, isAdminSpace, sectionMatchingCurrentRoute])

  const isSectionActive = (item: NavItem) =>
    item.type === 'section' && openSection === item.key

  const handleExpandSection = (sectionKey: string) => {
    const next = openSection === sectionKey ? null : sectionKey
    if (next) {
      dispatch(setSideNavOpenSection(next))
    }
    setOpenSection(next)
  }

  return (
    <div className={styles['sidebar']}>
      {/* SCROLLABLE CONTENT */}
      <ul className={styles['sidebar-list']}>
        {mainItems.map((item) => (
          <RenderNavItem
            key={item.key}
            item={item}
            isOpen={isSectionActive(item)}
            onToggleButtonClick={() => handleExpandSection(item.key)}
          />
        ))}
      </ul>

      {/* FOOTER */}
      {footerItems && (
        <>
          {/* SEPARATOR */}
          <div aria-hidden="true" className={styles['separator']}>
            <div className={styles['separator-line']} />
          </div>

          <div className={styles['footer']}>
            <ul>
              <li className={styles['review']}>
                <UserReviewDialog isAdminSpace={isAdminSpace} />
              </li>
              <li>
                <HelpDropdownNavItem isMobileScreen={isMobileScreen ?? false} />
              </li>
            </ul>
          </div>
        </>
      )}
    </div>
  )
}
