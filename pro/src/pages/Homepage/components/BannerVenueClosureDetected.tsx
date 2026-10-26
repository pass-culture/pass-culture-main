import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

export const BannerVenueClosureDetected = (): JSX.Element => (
  <Banner
    variant={BannerVariants.WARNING}
    title="Votre structure n’est plus à jour, merci d’en modifier le SIRET ou d’en demander la fermeture depuis vos paramètres."
  />
)
