import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

const HOW_TO_CANCEL_EVENT_URL =
  'https://aide.passculture.app/hc/fr/articles/4411992053649--Acteurs-Culturels-Comment-annuler-ou-reporter-un-%C3%A9v%C3%A9nement-'

export const StocksCalendarCancelBanner = () => (
  <Banner
    title=""
    actions={[
      {
        href: HOW_TO_CANCEL_EVENT_URL,
        label: 'Comment reporter ou annuler un évènement ?',
        isExternal: true,
        icon: fullLinkIcon,
        iconAlt: 'Nouvelle fenêtre',
        type: 'link',
      },
    ]}
    description="Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement. Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible."
  />
)
