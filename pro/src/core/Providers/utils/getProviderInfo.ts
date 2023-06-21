import allocineLogo from '../logos/logo-allocine.svg'
import boostLogo from '../logos/logo-boost.svg'
import cdiBookshopLogo from '../logos/logo-cdi-bookshop.svg'
import cgrLogo from '../logos/logo-cgr.svg'
import cineDigitalServiceLogo from '../logos/logo-cine-digital-service.svg'
import decitreLogo from '../logos/logo-decitre.svg'
import fnacLogo from '../logos/logo-fnac.svg'
import librairesLogo from '../logos/logo-libraires.svg'
import librisoftLogo from '../logos/logo-librisoft.svg'
import passCultureLogo from '../logos/logo-pass-culture-dark.svg'
import praxielLogo from '../logos/logo-praxiel.svg'
import titeLiveLogo from '../logos/logo-titeLive.svg'
import tmicEllipsesLogo from '../logos/logo-tmic-ellipses.svg'
import { ProviderInfo } from '../types'

export const getProviderInfo = (
  providerName: string
): ProviderInfo | undefined => {
  const providers: ProviderInfo[] = [
    {
      id: 'allociné',
      logo: allocineLogo,
      name: 'Allociné',
      synchronizedOfferMessage: 'Offre synchronisée avec Allociné',
    },
    {
      id: 'leslibraires.fr',
      logo: librairesLogo,
      name: 'Leslibraires.fr',
      synchronizedOfferMessage: 'Offre synchronisée avec Leslibraires.fr',
    },
    {
      id: 'titelive',
      logo: titeLiveLogo,
      name: 'Tite Live',
      synchronizedOfferMessage: 'Offre synchronisée avec Tite Live',
    },
    {
      id: 'fnac',
      logo: fnacLogo,
      name: 'Fnac',
      synchronizedOfferMessage: 'Offre synchronisée avec Fnac',
    },
    {
      id: 'mollat',
      logo: cdiBookshopLogo,
      name: 'Mollat',
      synchronizedOfferMessage: 'Offre synchronisée avec Mollat',
    },
    {
      id: 'cdi-bookshop',
      logo: cdiBookshopLogo,
      name: 'CDI-Bookshop',
      synchronizedOfferMessage: 'Offre synchronisée avec CDI-Bookshop',
    },
    {
      id: 'tmic-ellipses',
      logo: tmicEllipsesLogo,
      name: 'TMIC Ellipses',
      synchronizedOfferMessage: 'Offre synchronisée avec TMIC Ellipses',
    },
    {
      id: 'praxiel',
      logo: praxielLogo,
      name: 'Praxiel',
      synchronizedOfferMessage: 'Offre synchronisée avec Praxiel',
    },
    {
      id: 'librisoft',
      logo: librisoftLogo,
      name: 'Librisoft',
      synchronizedOfferMessage: 'Offre synchronisée avec Librisoft',
    },
    {
      id: 'decitre',
      logo: decitreLogo,
      name: 'Decitre',
      synchronizedOfferMessage: 'Offre synchronisée avec Decitre',
    },
    {
      id: 'pass',
      logo: passCultureLogo,
      name: 'Pass Culture API Stocks',
      synchronizedOfferMessage: 'Offre importée automatiquement',
    },
    {
      id: 'individual offers public api',
      logo: passCultureLogo,
      name: 'API Offres Individuelles',
      synchronizedOfferMessage: 'Offre importée automatiquement',
    },
    {
      id: 'ciné office',
      logo: cineDigitalServiceLogo,
      name: 'Ciné Office',
      synchronizedOfferMessage: 'Offre synchronisée avec Ciné Office',
    },
    {
      id: 'boost',
      logo: boostLogo,
      name: 'Boost',
      synchronizedOfferMessage: 'Offre synchronisée avec Boost',
    },
    {
      id: 'cgr',
      logo: cgrLogo,
      name: 'CGR',
      synchronizedOfferMessage: 'Offre synchronisée avec CGR',
    },
  ]

  return providers.find(providerInfo =>
    providerName.toLowerCase().startsWith(providerInfo.id)
  )
}
