import React from 'react'

import strokeShowIcon from 'icons/stroke-show.svg'
import Banner from 'ui-kit/Banners/Banner'

const BannerCreateOfferAdmin = (): JSX.Element => (
  <Banner
    type="attention"
    links={[
      {
        href: '/accueil',
        linkTitle: 'Aller à l’accueil',
        icon: strokeShowIcon,
        isExternal: false,
      },
    ]}
  >
    Afin de créer une offre en tant qu’administrateur veuillez sélectionner une
    structure.
  </Banner>
)

export default BannerCreateOfferAdmin
