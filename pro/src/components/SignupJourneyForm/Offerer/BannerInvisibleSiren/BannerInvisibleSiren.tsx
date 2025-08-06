import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from './BannerInvisibleSiren.module.scss'

interface BannerInvisibleSirenProps {
  isNewOnboarding?: boolean
}

export const BannerInvisibleSiren = ({
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
