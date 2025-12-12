import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './BannerInvisibleSiren.module.scss'

export const BannerInvisibleSiren = (): JSX.Element => (
  <div className={styles.banner}>
    <Banner
      title="SIRET non visible"
      actions={[
        {
          href: 'https://statut-diffusion-sirene.insee.fr/',
          label: `Modifier la visibilité de mon SIRET`,
          isExternal: true,
          icon: fullLinkIcon,
          iconAlt: 'Nouvelle fenêtre',
          type: 'link',
        },
      ]}
      variant={BannerVariants.ERROR}
      description="Pour valider votre inscription, rendez votre SIRET visible sur le site de l'INSEE."
    />
  </div>
)
