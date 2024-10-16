import { screen } from '@testing-library/react'

import {
  GetIndividualOfferWithAddressResponseModel,
  WithdrawalTypeEnum,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { IndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { AddressResponseIsLinkedToVenueModelFactory } from 'commons/utils/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
} from 'commons/utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { UsefulInformationsSummaryScreen } from '../UsefulInformationsSummary'

const renderUsefulInformationsSummaryScreen = (
  offer: GetIndividualOfferWithAddressResponseModel,
  options?: RenderWithProvidersOptions
) => {
  const contextValue = individualOfferContextValuesFactory({
    offer,
  })

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <UsefulInformationsSummaryScreen offer={offer} />
    </IndividualOfferContext.Provider>,
    {
      ...options,
    }
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

  it('should render summary with right field with OA FF', async () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      address: {
        ...AddressResponseIsLinkedToVenueModelFactory({
          label: 'mon adresse',
          city: 'ma ville',
          street: 'ma street',
          postalCode: '1',
        }),
      },
    })

    renderUsefulInformationsSummaryScreen(offer, {
      features: ['WIP_ENABLE_OFFER_ADDRESS'],
    })

    expect(
      await screen.findByText('Localisation de l’offre')
    ).toBeInTheDocument()
  })
})
