import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { IndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { AddressResponseIsLinkedToVenueModelFactory } from 'utils/commonOffersApiFactories'
import {
  categoryFactory,
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'

import { DetailsSummaryScreen } from '../DetailsSummary'

const renderDetailsSummaryScreen = (
  offer: GetIndividualOfferWithAddressResponseModel,
  options?: RenderWithProvidersOptions
) => {
  const categories = [
    categoryFactory({
      id: 'A',
      proLabel: 'Catégorie A',
      isSelectable: true,
    }),
  ]
  const subcategories = [
    subcategoryFactory({
      id: 'virtual',
      categoryId: 'A',
      proLabel: 'Sous catégorie online de A',
      isEvent: false,
      canBeDuo: false,
      onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
    }),
    subcategoryFactory({
      id: SubcategoryIdEnum.SEANCE_CINE,
      categoryId: 'A',
      proLabel: 'Sous catégorie offline de A',
      isEvent: false,
      conditionalFields: ['ean'],
      canBeDuo: true,
      canBeEducational: false,
      canBeWithdrawable: false,
      onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
    }),
  ]
  const contextValue = individualOfferContextValuesFactory({
    offer,
    categories,
    subCategories: subcategories,
  })

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <DetailsSummaryScreen offer={offer} />
    </IndividualOfferContext.Provider>,
    {
      ...options,
    }
  )
}

describe('DetailsSummaryScreen', () => {
  it('should render summary with filled data', () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
    })

    renderDetailsSummaryScreen(offer)

    expect(screen.getAllByText('Offre de test')).toHaveLength(2)
    expect(screen.getByText('Mon Lieu')).toBeInTheDocument()
    expect(screen.getByText('Catégorie A')).toBeInTheDocument()
    expect(screen.getByText('1234567891234')).toBeInTheDocument()
    expect(screen.getByText(/Modifier/)).toBeInTheDocument()
  })

  describe('when the offer is product based', () => {
    beforeEach(() => {
      const offer = getIndividualOfferFactory({
        name: 'Offre de test',
        subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
        productId: 1234567891234,
      })

      renderDetailsSummaryScreen(offer)
    })

    it('should display a callout telling that details cannot be edited', () => {
      expect(
        screen.getByText(
          /Les informations de cette page ne sont pas modifiables/
        )
      ).toBeInTheDocument()
    })

    it('should not display an edit button', () => {
      const editButton = screen.queryByText(/Modifier/)
      expect(editButton).not.toBeInTheDocument()
    })
  })

  it('should have "Qui propose l’offre ?" section if WIP_ENABLE_OFFER_ADDRESS FF is active', async () => {
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

    renderDetailsSummaryScreen(offer, {
      features: ['WIP_ENABLE_OFFER_ADDRESS'],
    })

    expect(await screen.findByText(/Qui propose l’offre/)).toBeInTheDocument()
  })
})
