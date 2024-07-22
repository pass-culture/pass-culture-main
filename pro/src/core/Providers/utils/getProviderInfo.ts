import allocineLogo from '../logos/logo-allocine.svg'
import boostLogo from '../logos/logo-boost.svg'
import cdiBookshopLogo from '../logos/logo-cdi-bookshop.svg'
import cgrLogo from '../logos/logo-cgr.svg'
import cineDigitalServiceLogo from '../logos/logo-cine-digital-service.svg'
import decitreLogo from '../logos/logo-decitre.svg'
import emsLogo from '../logos/logo-ems.svg'
import fnacLogo from '../logos/logo-fnac.svg'
import librairesLogo from '../logos/logo-libraires.svg'
import librisoftLogo from '../logos/logo-librisoft.svg'
import passCultureLogo from '../logos/logo-pass-culture-dark.svg'
import praxielLogo from '../logos/logo-praxiel.svg'
import titeLiveLogo from '../logos/logo-titeLive.svg'
import tmicEllipsesLogo from '../logos/logo-tmic-ellipses.svg'
import { ProviderInfo } from '../types'

const PROVIDERS_LOGOS: Array<{ id: string; logo: string }> = [
  { id: 'allociné', logo: allocineLogo },
  { id: 'leslibraires.fr', logo: librairesLogo },
  { id: 'titelive', logo: titeLiveLogo },
  { id: 'fnac', logo: fnacLogo },
  { id: 'mollat', logo: cdiBookshopLogo },
  { id: 'cdi-bookshop', logo: cdiBookshopLogo },
  { id: 'tmic-ellipses', logo: tmicEllipsesLogo },
  { id: 'praxiel', logo: praxielLogo },
  { id: 'librisoft', logo: librisoftLogo },
  { id: 'decitre', logo: decitreLogo },
  { id: 'ciné office', logo: cineDigitalServiceLogo },
  { id: 'boost', logo: boostLogo },
  { id: 'cgr', logo: cgrLogo },
  { id: 'ems', logo: emsLogo },
]

export const getProviderInfo = (
  providerName: string
): ProviderInfo | undefined => {
  if (!providerName) {
    return
  }

  // Specific case for offers created using the old public Stock API (`/v2/venue/{venue_id}/stocks`)
  if (providerName === 'Pass Culture API Stocks') {
    return {
      id: 'individual offers public api',
      logo: passCultureLogo,
      name: 'API Offres Individuelles',
      synchronizedOfferMessage: 'Offre importée automatiquement',
    }
  }

  const providerLogo = PROVIDERS_LOGOS.find(({ id }) =>
    providerName.toLowerCase().startsWith(id)
  )

  return {
    id: providerName.toLowerCase(),
    logo: providerLogo ? providerLogo.logo : '',
    name: providerName,
    synchronizedOfferMessage: `Offre synchronisée avec ${providerName}`,
  }
}
