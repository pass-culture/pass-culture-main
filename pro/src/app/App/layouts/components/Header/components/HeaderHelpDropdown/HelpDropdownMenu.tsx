import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'

import dropdownStyles from '../HeaderDropdown/HeaderDropdown.module.scss'

export const HelpDropdownMenu = () => {
  const { logEvent } = useAnalytics()
  return (
    <>
      <DropdownMenu.Item className={dropdownStyles['menu-item']}>
        <Button
          to="https://aide.passculture.app"
          as="a"
          isExternal
          opensInNewTab
          icon={fullLinkIcon}
          onClick={() =>
            logEvent(Events.CLICKED_CONSULT_HELP, {
              from: location.pathname,
            })
          }
          label="Consulter le centre d'aide"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
        />
      </DropdownMenu.Item>
      <DropdownMenu.Item className={dropdownStyles['menu-item']}>
        <Button
          as="a"
          icon={fullLinkIcon}
          to="https://aide.passculture.app/hc/fr/articles/13155602579356--Acteurs-Culturels-Quelle-%C3%A9quipe-contacter-selon-votre-demande"
          isExternal
          opensInNewTab
          onClick={() =>
            logEvent(Events.CLICKED_CONTACT_OUR_TEAMS, {
              from: location.pathname,
            })
          }
          label="Contacter nos équipes"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
        />
      </DropdownMenu.Item>
      <DropdownMenu.Item className={dropdownStyles['menu-item']}>
        <Button
          as="a"
          icon={fullLinkIcon}
          to="https://passcultureapp.notion.site/db6b4a9f5fc84fb28626cfeb18d20340?v=19911882c20b4bb39524825164fcf3c2"
          isExternal
          opensInNewTab
          onClick={() =>
            logEvent(Events.CLICKED_NEW_EVOLUTIONS, {
              from: location.pathname,
            })
          }
          label="Découvrir les nouveautés"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
        />
      </DropdownMenu.Item>
      <DropdownMenu.Item className={dropdownStyles['menu-item']}>
        <Button
          as="a"
          icon={fullLinkIcon}
          to="https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0"
          isExternal
          opensInNewTab
          onClick={() =>
            logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES, {
              from: location.pathname,
            })
          }
          label="Bonnes pratiques et études"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
        />
      </DropdownMenu.Item>
    </>
  )
}
