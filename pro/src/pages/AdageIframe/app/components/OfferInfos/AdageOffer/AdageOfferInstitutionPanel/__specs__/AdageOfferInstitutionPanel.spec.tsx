import { screen } from '@testing-library/react'

import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser, defaultCollectiveOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  AdageOfferInstitutionPanel,
  AdageOfferInstitutionPanelProps,
} from '../AdageOfferInstitutionPanel'

function renderAdageOfferInstitutionPanel(
  props: AdageOfferInstitutionPanelProps = {
    offer: defaultCollectiveOffer,
    adageUser: defaultAdageUser,
    isPreview: false,
  }
) {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <AdageOfferInstitutionPanel {...props} />
    </AdageUserContextProvider>
  )
}

describe('AdageOfferPartnerPanel', () => {
  it('should render the instution panel', () => {
    renderAdageOfferInstitutionPanel()

    expect(
      screen.getByRole('heading', { name: 'Offre adressée à :' })
    ).toBeInTheDocument()

    expect(screen.getByText('À préréserver')).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: /Préréserver l’offre/ })
    ).toBeInTheDocument()
  })

  it("should not show the booking limit date if it's not available", () => {
    renderAdageOfferInstitutionPanel({
      offer: {
        ...defaultCollectiveOffer,
        stock: {
          ...defaultCollectiveOffer.stock,
          bookingLimitDatetime: undefined,
        },
      },
      adageUser: defaultAdageUser,
      isPreview: false,
    })

    expect(screen.queryByText('À préréserver')).not.toBeInTheDocument()
  })
})
