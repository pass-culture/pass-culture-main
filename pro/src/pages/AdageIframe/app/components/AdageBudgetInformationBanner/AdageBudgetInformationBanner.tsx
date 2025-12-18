import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

export const AdageBudgetInformationBanner = () => {
  return (
    <Banner
      title="Informations sur les crédits 2026"
      description={
        "Les crédits pass Culture de votre établissement pour la deuxième période de l'année scolaire 2025-2026 ne sont pas encore disponibles. Vous ne pouvez donc pas réserver d'actions payantes. Les réservations d'actions gratuites et les prises de contact avec des partenaires culturels sont toujours possibles."
      }
      variant={BannerVariants.WARNING}
    />
  )
}
