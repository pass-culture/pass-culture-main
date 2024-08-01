import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { IndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { addressResponseIsEditableModelFactory } from 'utils/commonOffersApiFactories'
import {
  categoryFactory,
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DetailsSummaryScreen } from '../DetailsSummary'

const renderDetailsSummaryScreen = (
  offer: GetIndividualOfferWithAddressResponseModel,
  feature: string[] = []
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
      features: feature,
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
    expect(
      screen.getByText('Chuck n’est pas identifiable par un EAN')
    ).toBeInTheDocument()
  })

  it('should render summary with right field with OA FF', async () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      address: {
        ...addressResponseIsEditableModelFactory({
          label: 'mon adresse',
          city: 'ma ville',
          street: 'ma street',
          postalCode: '1',
        }),
      },
    })

    renderDetailsSummaryScreen(offer, ['WIP_ENABLE_OFFER_ADDRESS'])

    expect(await screen.findByText(/Qui propose l’offre/)).toBeInTheDocument()
    expect(
      await screen.findByText('Localisation de l’offre')
    ).toBeInTheDocument()
  })
})
