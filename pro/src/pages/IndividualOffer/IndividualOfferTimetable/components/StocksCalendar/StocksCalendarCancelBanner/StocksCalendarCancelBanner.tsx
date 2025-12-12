import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

const HOW_TO_CANCEL_EVENT_URL =
  'https://aide.passculture.app/hc/fr/articles/4411992053649--Acteurs-Culturels-Comment-annuler-ou-reporter-un-%C3%A9v%C3%A9nement-'

export const StocksCalendarCancelBanner = () => (
  <Banner
    title="Délai d'annulation"
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
    description="Les bénéficiaires peuvent annuler jusqu'à 48h avant l'événement. Pour annuler un événement, supprimez la ligne de stock (action irréversible)."
  />
)
