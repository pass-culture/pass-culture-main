export interface ILegacyRedirect {
  redirectFrom: string
  redirectTo: string
}

interface IGetLegacyRedirectArgs {
  isV2: boolean
}

const getLegacyRedirect = ({
  isV2 = false,
}: IGetLegacyRedirectArgs): ILegacyRedirect[] => [
  {
    redirectFrom: '/offres/:offerId([A-Z0-9]+)/edition',
    redirectTo: isV2
      ? '/offre/:offerId([A-Z0-9]+)/individuel/recapitulatif'
      : '/offre/:offerId([A-Z0-9]+)/v3/individuelle/recapitulatif',
  },
  {
    redirectFrom: '/offre/:offerId([A-Z0-9]+)/scolaire/edition',
    redirectTo: '/offre/:offerId([A-Z0-9]+)/collectif/edition',
  },
]

export default getLegacyRedirect
