import React from 'react'

import { ReactComponent as IcoEyeOpen } from 'icons/ico-eye-full-open.svg'
import Banner from 'ui-kit/Banners/Banner'

const BannerCreateOfferAdmin = (): JSX.Element => (
  <Banner
    type="attention"
    links={[
      {
        href: '/structures',
        linkTitle: 'Aller à la liste des structures',
        Icon: IcoEyeOpen,
      },
    ]}
  >
    Afin de créer une offre en tant qu’administrateur veuillez sélectionner une
    structure.
  </Banner>
)

export default BannerCreateOfferAdmin
