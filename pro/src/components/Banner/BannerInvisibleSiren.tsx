import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'

import styles from './BannerInvisibleSiren.module.scss'

interface BannerInvisibleSirenProps {
  isNewOnboarding?: boolean
}

const BannerInvisibleSiren = ({
  isNewOnboarding = false,
}: BannerInvisibleSirenProps): JSX.Element => (
  <Callout
    links={[
      {
        href: 'https://statut-diffusion-sirene.insee.fr/',
        label: `Modifier la visibilité de mon ${
          isNewOnboarding ? 'SIRET' : 'SIREN'
        }`,
        isExternal: true,
      },
    ]}
    variant={CalloutVariant.ERROR}
    className={styles.banner}
  >
    Le {isNewOnboarding ? 'SIRET' : 'SIREN'} doit être rendu visible pour
    valider votre inscription. Vous pouvez effectuer cette démarche sur le site
    de l’INSEE.
  </Callout>
)

export default BannerInvisibleSiren
