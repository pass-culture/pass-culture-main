import React from 'react'

import strokeShowIcon from 'icons/stroke-show.svg'
import { Banner } from 'ui-kit'

const BannerCreateOfferAdmin = (): JSX.Element => (
  <Banner
    type="attention"
    links={[
      {
        href: '/accueil',
        label: 'Aller à l’accueil',
        icon: { src: strokeShowIcon, alt: '' },
        isExternal: false,
      },
    ]}
  >
    Afin de créer une offre en tant qu’administrateur veuillez sélectionner une
    structure.
  </Banner>
)

export default BannerCreateOfferAdmin
