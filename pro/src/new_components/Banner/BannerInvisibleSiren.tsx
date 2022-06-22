import Banner from 'ui-kit/Banner'
import React from 'react'

const BannerInvisibleSiren = (): JSX.Element => (
  <Banner
    href="https://statut-diffusion-sirene.insee.fr/"
    linkTitle="Modifier la visibilité de mon SIREN"
    type="attention"
  >
    Le SIREN doit être rendu visible pour valider votre inscription. Vous pouvez
    effectuer cette démarche sur le site de l’INSEE.
  </Banner>
)

export default BannerInvisibleSiren
