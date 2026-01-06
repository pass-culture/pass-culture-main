import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

export const CollectiveBudgetBanner = () => {
  const bannerDisplayTargetDate = new Date('2026-01-01').getTime()
  const currentDate = Date.now()

  if (currentDate < bannerDisplayTargetDate) {
    return null
  }

  return (
    <Banner
      title={'Part collective du pass Culture 2026'}
      description={
        "Les collèges et lycées du ministère de l'Éducation nationale ne connaissent pas encore leurs crédits de dépense pass Culture pour la deuxième période de l'année scolaire 2025-2026. Ils ne peuvent donc pas réserver d'offres payantes actuellement. Les réservations d'offres gratuites sont toujours possibles."
      }
      variant={BannerVariants.WARNING}
    />
  )
}
