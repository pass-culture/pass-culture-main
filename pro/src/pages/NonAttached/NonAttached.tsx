import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { Newsletter } from '@/components/Newsletter/Newsletter'
import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './NonAttached.module.scss'

export const NonAttached = () => {
  return (
    <OnboardingLayout
      isEntryScreen
      mainHeading="Bienvenue sur votre espace partenaire"
    >
      <div className={styles['wrapper']}>
        <Banner
          title="Votre rattachement est en cours de traitement par les équipes du pass Culture"
          actions={[
            {
              href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
              label: 'En savoir plus',
              icon: fullLinkIcon,
              iconAlt:
                'Acteurs Culturels: s’inscrire et comprendre le fonctionnement (Nouvelle fenêtre, site https://aide.passculture.app)',
              isExternal: true,
              type: 'link',
            },
          ]}
          description="Un email vous sera envoyé lors de la validation de votre rattachement. Vous aurez alors accès à l’ensemble des fonctionnalités du pass Culture Pro."
        />
        <br />
        <Newsletter />
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = NonAttached
