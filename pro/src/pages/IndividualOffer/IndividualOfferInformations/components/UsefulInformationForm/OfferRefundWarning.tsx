import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

export const OfferRefundWarning = () => {
  return (
    <Callout
      links={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/6043184068252',
          isExternal: true,
          label:
            'Quelles sont les offres numériques éligibles au remboursement ?',
        },
      ]}
      variant={CalloutVariant.WARNING}
    >
      Cette offre numérique ne sera pas remboursée.
    </Callout>
  )
}
