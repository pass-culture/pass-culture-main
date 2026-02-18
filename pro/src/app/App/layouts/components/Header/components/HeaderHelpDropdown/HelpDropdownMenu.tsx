import { Link } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import fullLinkIcon from '@/icons/full-link.svg'
import { DropdownItem } from '@/ui-kit/Dropdown/DropdownItem'

export const HelpDropdownMenu = () => {
  const { logEvent } = useAnalytics()

  return (
    <>
      <DropdownItem
        icon={fullLinkIcon}
        onSelect={() =>
          logEvent(Events.CLICKED_CONSULT_HELP, {
            from: location.pathname,
          })
        }
      >
        <Link target="_blank" to={'https://aide.passculture.app'}>
          Consulter le centre d’aide
        </Link>
      </DropdownItem>
      <DropdownItem
        icon={fullLinkIcon}
        onSelect={() =>
          logEvent(Events.CLICKED_CONTACT_OUR_TEAMS, {
            from: location.pathname,
          })
        }
      >
        <Link
          target="_blank"
          to="https://aide.passculture.app/hc/fr/articles/13155602579356--Acteurs-Culturels-Quelle-%C3%A9quipe-contacter-selon-votre-demande"
        >
          Contacter nos équipes
        </Link>
      </DropdownItem>
      <DropdownItem
        icon={fullLinkIcon}
        onSelect={() =>
          logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES, {
            from: location.pathname,
          })
        }
      >
        <Link
          target="_blank"
          to="https://passcultureapp.notion.site/db6b4a9f5fc84fb28626cfeb18d20340?v=19911882c20b4bb39524825164fcf3c2"
        >
          Découvrir les nouveautés
        </Link>
      </DropdownItem>
      <DropdownItem
        icon={fullLinkIcon}
        onSelect={() =>
          logEvent(Events.CLICKED_NEW_EVOLUTIONS, {
            from: location.pathname,
          })
        }
      >
        <Link
          target="_blank"
          to="https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0"
        >
          Bonnes pratiques et études
        </Link>
      </DropdownItem>
    </>
  )
}
