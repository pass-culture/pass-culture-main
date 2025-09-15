import { Callout } from '@/ui-kit/Callout/Callout'

const HOW_TO_CANCEL_EVENT_URL =
  'https://aide.passculture.app/hc/fr/articles/4411992053649--Acteurs-Culturels-Comment-annuler-ou-reporter-un-%C3%A9v%C3%A9nement-'

export const StocksCalendarCancelBanner = () => (
  <Callout
    links={[
      {
        href: HOW_TO_CANCEL_EVENT_URL,
        label: 'Comment reporter ou annuler un évènement ?',
        isExternal: true,
      },
    ]}
  >
    Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas
    le faire à moins de 48h de l’évènement. Vous pouvez annuler un évènement en
    supprimant la ligne de stock associée. Cette action est irréversible.
  </Callout>
)
