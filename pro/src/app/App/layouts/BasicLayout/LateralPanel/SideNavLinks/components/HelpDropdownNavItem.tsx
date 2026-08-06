import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Dropdown } from '@/design-system/Dropdown/Dropdown'
import fullHelpIcon from '@/icons/full-help.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import fullRightIcon from '@/icons/full-right.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './HelpDropdownNavItem.module.scss'

interface HelpDropdownNavItemProps {
  isMobileScreen: boolean
}

export const HelpDropdownNavItem = ({
  isMobileScreen,
}: HelpDropdownNavItemProps) => {
  const { logEvent } = useAnalytics()

  return (
    <Dropdown
      label="Centre d’aide"
      side={isMobileScreen ? 'top' : 'right'}
      trigger={
        // The DS does not allow two icons in the same button
        <button type="button" className={styles['nav-links-help']}>
          <div className={styles['nav-links-help-content']}>
            <SvgIcon src={fullHelpIcon} alt="" width="22" />
            Centre d’aide
          </div>
          <SvgIcon src={fullRightIcon} alt="" width="18" />
        </button>
      }
      items={[
        [
          {
            icon: fullLinkIcon,
            text: 'Consulter le centre d’aide',
            link: {
              to: 'https://aide.passculture.app',
              opensInNewTab: true,
              onClick: () => logEvent(Events.CLICKED_CONSULT_HELP),
            },
          },
          {
            icon: fullLinkIcon,
            text: 'Contacter nos équipes',
            link: {
              to: 'https://aide.passculture.app/hc/fr/articles/13155602579356--Acteurs-Culturels-Quelle-%C3%A9quipe-contacter-selon-votre-demande',
              opensInNewTab: true,
              onClick: () => logEvent(Events.CLICKED_CONTACT_OUR_TEAMS),
            },
          },
          {
            icon: fullLinkIcon,
            text: 'Découvrir les nouveautés',
            link: {
              to: 'https://passcultureapp.notion.site/db6b4a9f5fc84fb28626cfeb18d20340?v=19911882c20b4bb39524825164fcf3c2',
              opensInNewTab: true,
              onClick: () => logEvent(Events.CLICKED_NEW_EVOLUTIONS),
            },
          },
          {
            icon: fullLinkIcon,
            text: 'Bonnes pratiques et études',
            link: {
              to: 'https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0',
              opensInNewTab: true,
              onClick: () => logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES),
            },
          },
        ],
      ]}
    />
  )
}
