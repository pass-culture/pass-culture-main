import { useState } from 'react'
import { useLocation } from 'react-router'

import {
  LAPTOP_MEDIA_QUERY,
  useMediaQuery,
} from '@/commons/hooks/useMediaQuery'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullSmsIcon from '@/icons/full-sms.svg'

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

  const sections = mainItems.filter((i) => i.type === 'section')
  const firstSectionKey = sections[0]?.key ?? null

  // BasicLayout remounts on every navigation so we use pathName to keep the right section open
  const getSectionFromRoute = (): string | null => {
    const sectionMatchingCurrentRoute = sections.find((section) =>
      section.children?.some((child) => child.to === location.pathname)
    )

    if (sectionMatchingCurrentRoute) {
      sessionStorage.setItem(
        'sideNavOpenSection',
        sectionMatchingCurrentRoute.key
      )
      return sectionMatchingCurrentRoute.key
    }

    const lastOpenSection = sessionStorage.getItem('sideNavOpenSection')
    if (lastOpenSection) {
      return lastOpenSection
    }
    return null
  }

  const [openSection, setOpenSection] = useState<string | null>(
    isAdminSpace ? firstSectionKey : getSectionFromRoute
  )

  const isSectionActive = (item: NavItem) =>
    item.type === 'section' && openSection === item.key

  const handleExpandSection = (sectionKey: string) => {
    const next = openSection === sectionKey ? null : sectionKey
    if (next) sessionStorage.setItem('sideNavOpenSection', next)
    setOpenSection(next)
  }

  return (
    <div className={styles['sidebar']}>
      {/* SCROLLABLE CONTENT */}
      <ul>
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
      <div className={styles['footer']}>
        {footerItems && (
          <div>
            <div aria-hidden="true">
              <div className={styles['separator-line']} />
            </div>
            <ul>
              <li className={styles['review']}>
                <UserReviewDialog
                  dialogTrigger={
                    <Button
                      icon={fullSmsIcon}
                      label="Donner mon avis"
                      variant={ButtonVariant.TERTIARY}
                      color={ButtonColor.NEUTRAL}
                    />
                  }
                  isAdminSpace={isAdminSpace}
                />
              </li>
              <li>
                <HelpDropdownNavItem isMobileScreen={isMobileScreen ?? false} />
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
