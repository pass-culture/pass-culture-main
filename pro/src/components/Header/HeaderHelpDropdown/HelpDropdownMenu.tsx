import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'

import dropdownStyles from '../HeaderDropdown/HeaderDropdown.module.scss'

export const HelpDropdownMenu = () => {
  const { logEvent } = useAnalytics()
  return (
    <>
      <DropdownMenu.Item className={dropdownStyles['menu-item']} asChild>
        <ButtonLink
          to="https://aide.passculture.app"
          isExternal
          opensInNewTab
          icon={fullLinkIcon}
          onClick={() =>
            logEvent(Events.CLICKED_HELP_CENTER, {
              from: location.pathname,
            })
          }
        >
          Consulter le centre d’aide
        </ButtonLink>
      </DropdownMenu.Item>
      <DropdownMenu.Item className={dropdownStyles['menu-item']} asChild>
        <ButtonLink
          icon={fullLinkIcon}
          to="https://aide.passculture.app/hc/fr/articles/13155602579356--Acteurs-Culturels-Quelle-%C3%A9quipe-contacter-selon-votre-demande"
          isExternal
          opensInNewTab
          onClick={() =>
            logEvent(Events.CLICKED_CONTACT_OUR_TEAMS, {
              from: location.pathname,
            })
          }
        >
          Contacter nos équipes
        </ButtonLink>
      </DropdownMenu.Item>
      <DropdownMenu.Item className={dropdownStyles['menu-item']} asChild>
        <ButtonLink
          icon={fullLinkIcon}
          to="https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0"
          isExternal
          opensInNewTab
          onClick={() =>
            logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES, {
              from: location.pathname,
            })
          }
        >
          Bonnes pratiques et études
        </ButtonLink>
      </DropdownMenu.Item>
    </>
  )
}
