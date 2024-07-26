import { screen } from '@testing-library/react'

import {
  GetIndividualOfferWithAddressResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { IndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { UsefulInformationsSummaryScreen } from '../UsefulInformationsSummary'

const renderUsefulInformationsSummaryScreen = (
  offer: GetIndividualOfferWithAddressResponseModel
) => {
  const contextValue = individualOfferContextValuesFactory({
    offer,
  })

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <UsefulInformationsSummaryScreen offer={offer} />
    </IndividualOfferContext.Provider>
  )
}

describe('UsefulInformationsSummaryScreen', () => {
  it('should render summary with filled data', () => {
    const offer = getIndividualOfferFactory({
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      withdrawalDelay: 120,
      bookingContact: 'robert@exemple.com',
      venue: { ...getOfferVenueFactory(), isVirtual: true },
      url: 'https://www.example.com',
    })

    renderUsefulInformationsSummaryScreen(offer)

    expect(screen.getByText(/Informations de retrait/)).toBeInTheDocument()
    expect(
      screen.getByText('Retrait sur place (guichet, comptoir...)')
    ).toBeInTheDocument()
    expect(
      screen.getByText('2 minutes avant le début de l’évènement')
    ).toBeInTheDocument()
    expect(screen.getByText('robert@exemple.com')).toBeInTheDocument()
    expect(screen.getByText('https://www.example.com')).toBeInTheDocument()
  })
})
