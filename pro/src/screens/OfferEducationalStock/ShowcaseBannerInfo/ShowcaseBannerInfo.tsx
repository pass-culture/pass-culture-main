import React from 'react'

import { Banner } from 'ui-kit'

const ShowcaseBannerInfo = (): JSX.Element => (
  <Banner
    type="notification-info"
    links={[
      {
        isExternal: true,
        href: 'https://aide.passculture.app/hc/fr/articles/4416082284945',
        label:
          'Consultez l’article “Quel est le cycle de vie de mon offre collective, de sa création à son remboursement ?”',
      },
    ]}
  >
    1) À sa création, votre offre vitrine sera visible sur ADAGE, la plateforme
    des enseignants
    <br />
    2) L’enseignant vous contactera pour discuter des détails de l’offre
    <br />
    3) Vous créerez une offre réservable en complétant la date, le prix et
    l’établissement vus avec l’enseignant
    <br />
    4) Une fois cette nouvelle offre publiée, elle sera préréservable sur ADAGE
    par l’enseignant
    <br />
  </Banner>
)

export default ShowcaseBannerInfo
