import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import fullSmsIcon from '@/icons/full-sms.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { HelpDropdownNavItem } from './components/HelpDropdownNavItem'
import { RenderNavItem } from './components/SideNavLink'
import { UserReviewDialog } from './components/UserReviewDialog/UserReviewDialog'
import styles from './SideNavLinks.module.scss'

type NavGroup = 'main' | 'footer'
export interface NavItem {
  key: string
  group: NavGroup
  type: string
  title?: string
  icon?: string
  to?: string
  children?: NavItem[]
}

export const SideNavLinks = ({
  navItems,
  withSwitchVenueFeature,
}: {
  navItems: NavItem[]
  withSwitchVenueFeature: boolean
}) => {
  const mainItems = navItems.filter((i) => i.group === 'main')
  const footerItems = navItems.filter((i) => i.group === 'footer')

  const isMobileScreen = useMediaQuery('(max-width: 64rem)')

  return (
    <div className={styles.sidebar}>
      {/* SCROLLABLE CONTENT */}
      <ul>
        {mainItems.map((item) => (
          <RenderNavItem key={item.key} item={item} />
        ))}
      </ul>

      {/* FOOTER */}
      <div className={styles.footer}>
        {footerItems && (
          <div>
            <div aria-hidden="true">
              <div className={styles['separator-line']} />
            </div>

            {withSwitchVenueFeature ? (
              <ul>
                <li>
                  <UserReviewDialog
                    dialogTrigger={
                      <div className={styles['nav-links-item']}>
                        <SvgIcon width="22" src={fullSmsIcon} />
                        Donner mon avis
                      </div>
                    }
                  />
                </li>
                <li>
                  <HelpDropdownNavItem
                    isMobileScreen={isMobileScreen ?? false}
                  />
                </li>
              </ul>
            ) : (
              <ul>
                {footerItems.map((item) => (
                  <RenderNavItem key={item.key} item={item} />
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
