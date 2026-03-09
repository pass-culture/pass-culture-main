import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

interface OfferEducationalModalProps {
  isIndividual?: boolean
}

export const DownloadsMovedBanner = ({
  isIndividual = false,
}: OfferEducationalModalProps) => {
  const bannerContent = isIndividual
    ? {
        title:
          'Télécharger vos réservations dans l’onglet “Données d’activité” de votre Espace Administration accessible en haut à droite.',
        label: 'Accéder à la page de téléchargement des réservations',
        href: '/administration/donnees-activite/individuel',
      }
    : {
        title:
          'Télécharger vos offres réservables dans l’onglet “Données d’activité” de votre Espace Administration accessible en haut à droite.',
        label: 'Accéder à la page de téléchargement des offres',
        href: '/administration/donnees-activite/collectif',
      }
  return (
    <Banner
      title={bannerContent.title}
      variant={BannerVariants.DEFAULT}
      actions={[
        {
          label: bannerContent.label,
          icon: fullNextIcon,
          href: bannerContent.href,
          type: 'link',
        },
      ]}
    />
  )
}
