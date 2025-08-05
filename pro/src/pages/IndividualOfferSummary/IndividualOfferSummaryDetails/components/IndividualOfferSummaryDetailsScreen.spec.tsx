import {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { screen } from '@testing-library/react'
import { IndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { getAddressResponseIsLinkedToVenueModelFactory } from 'commons/utils/factories/commonOffersApiFactories'
import {
  categoryFactory,
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { expect } from 'vitest'

import { IndividualOfferSummaryDetailsScreen } from './IndividualOfferSummaryDetailsScreen'

const renderIndividualOfferSummaryDetailsScreen = (
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
      <IndividualOfferSummaryDetailsScreen offer={offer} />
    </IndividualOfferContext.Provider>,
    {
      ...options,
    }
  )
}

describe('IndividualOfferSummaryDetailsScreen', () => {
  it('should render summary with filled data', () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
    })

    renderIndividualOfferSummaryDetailsScreen(offer)

    expect(screen.getAllByText('Offre de test')).toHaveLength(2)
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

      renderIndividualOfferSummaryDetailsScreen(offer)
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

  it('should have "Structure" section', () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      address: {
        ...getAddressResponseIsLinkedToVenueModelFactory({
          label: 'mon adresse',
          city: 'ma ville',
          street: 'ma street',
          postalCode: '1',
        }),
      },
      venue: getOfferVenueFactory({ publicName: undefined }),
    })

    renderIndividualOfferSummaryDetailsScreen(offer)

    expect(screen.getByText(/Structure/)).toBeInTheDocument()
    expect(screen.getByText(/Le nom du lieu/)).toBeInTheDocument()
  })

  it('should have "Structure" section with publicName', () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      address: {
        ...getAddressResponseIsLinkedToVenueModelFactory({
          label: 'mon adresse',
          city: 'ma ville',
          street: 'ma street',
          postalCode: '1',
        }),
      },
      venue: getOfferVenueFactory({ publicName: 'TATA' }),
    })

    renderIndividualOfferSummaryDetailsScreen(offer)

    expect(screen.getByText(/Structure/)).toBeInTheDocument()
    expect(screen.getByText('TATA')).toBeInTheDocument()
  })

  it('should show the description of the offer', () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      description: 'my description',
    })

    renderIndividualOfferSummaryDetailsScreen(offer)

    //  The description is displayed twice : once in the summary and once in the preview
    expect(screen.getAllByText('my description')).toHaveLength(2)
    expect(screen.getAllByTestId('markdown-content')).toHaveLength(2)
  })

  it('should not show the description if the offer has no description', () => {
    const offer = getIndividualOfferFactory({
      name: 'Offre de test',
      description: '',
    })

    renderIndividualOfferSummaryDetailsScreen(offer)

    expect(screen.queryByTestId('markdown-content')).not.toBeInTheDocument()
  })
})
