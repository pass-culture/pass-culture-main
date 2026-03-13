import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

export const VenueValidationBanner = () => {
  return (
    <Banner
      title="Votre structure est en cours de traitement par les équipes du pass Culture"
      actions={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-',
          label: 'En savoir plus sur le fonctionnement du pass Culture',
          isExternal: true,
          icon: fullLinkIcon,
          iconAlt: 'Nouvelle fenêtre',
          type: 'link',
        },
      ]}
      description={
        'Vos offres seront publiées sous réserve de validation de votre structure.'
      }
    />
  )
}
