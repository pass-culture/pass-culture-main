import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'

export const BannerCreateOfferAdmin = (): JSX.Element => (
  <Callout
    variant={CalloutVariant.INFO}
    links={[
      {
        href: '/accueil',
        label: 'Aller à l’accueil',
        isExternal: false,
      },
    ]}
  >
    Afin de créer une offre en tant qu’administrateur veuillez sélectionner une
    structure.
  </Callout>
)
