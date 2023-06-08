import React from 'react'

import Banner from 'ui-kit/Banners/Banner'

interface BannerInvisibleSirenProps {
  isNewOnboarding?: boolean
}

const BannerInvisibleSiren = ({
  isNewOnboarding = false,
}: BannerInvisibleSirenProps): JSX.Element => (
  <Banner
    links={[
      {
        href: 'https://statut-diffusion-sirene.insee.fr/',
        linkTitle: `Modifier la visibilité de mon ${
          isNewOnboarding ? 'SIRET' : 'SIREN'
        }`,
      },
    ]}
    type="attention"
  >
    Le {isNewOnboarding ? 'SIRET' : 'SIREN'} doit être rendu visible pour
    valider votre inscription. Vous pouvez effectuer cette démarche sur le site
    de l’INSEE.
  </Banner>
)

export default BannerInvisibleSiren
