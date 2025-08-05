import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { screen } from '@testing-library/react'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from 'commons/utils/factories/adageFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'

import { AdageOffer } from '../AdageOffer'

function renderAdageOffer({
  offer,
  isPreview = false,
}: {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
  isPreview?: boolean
}) {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <AdageOffer
        offer={offer}
        adageUser={defaultAdageUser}
        isPreview={isPreview}
      />
    </AdageUserContextProvider>
  )
}

describe('AdageOffer', () => {
  it('should display the offer information sections', () => {
    renderAdageOffer({ offer: defaultCollectiveTemplateOffer })

    expect(
      screen.getByRole('heading', { name: 'Détails de l’offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Public concerné' })
    ).toBeInTheDocument()
  })

  it('should show the offer cultural partner infos for a collective offer', () => {
    renderAdageOffer({ offer: defaultCollectiveTemplateOffer })

    expect(
      screen.getByRole('heading', { name: 'Partenaire culturel' })
    ).toBeInTheDocument()
  })

  it('should show the offer instistution panel for a collective bookable offer', () => {
    renderAdageOffer({ offer: defaultCollectiveOffer })

    expect(
      screen.getByRole('heading', { name: 'Offre adressée à :' })
    ).toBeInTheDocument()
  })
})
