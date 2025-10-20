import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
import { Footer } from '@/components/Footer/Footer'
import { Newsletter } from '@/components/Newsletter/Newsletter'
import { Callout } from '@/ui-kit/Callout/Callout'

export const NonAttached = () => {
  return (
    <FunnelLayout mainHeading="Bienvenue sur votre espace partenaire">
      <Callout
        links={[
          {
            href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
            label: 'En savoir plus',
            'aria-label':
              'Acteurs Culturels: s’inscrire et comprendre le fonctionnement (Nouvelle fenêtre, site https://aide.passculture.app)',
            isExternal: true,
          },
        ]}
      >
        <strong>
          Votre rattachement est en cours de traitement par les équipes du pass
          Culture
        </strong>
        <br />
        Un email vous sera envoyé lors de la validation de votre rattachement.
        Vous aurez alors accès à l’ensemble des fonctionnalités du pass Culture
        Pro.
      </Callout>
      <br />
      <Newsletter />
      <Footer layout={'basic'} />
    </FunnelLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = NonAttached
