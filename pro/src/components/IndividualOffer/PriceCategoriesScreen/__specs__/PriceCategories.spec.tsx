import { screen } from '@testing-library/react'

import { OfferStatus } from '@/apiClient//v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  PriceCategoriesScreen,
  PriceCategoriesScreenProps,
} from '../PriceCategoriesScreen'

const renderPriceCategories = (props: PriceCategoriesScreenProps) =>
  renderWithProviders(<PriceCategoriesScreen {...props} />)

describe('PriceCategories', () => {
  it('should render without error', () => {
    renderPriceCategories({ offer: getIndividualOfferFactory() })

    expect(screen.getByText('Tarifs')).toBeInTheDocument()
  })

  it('should not disabled field for allociné', () => {
    renderPriceCategories({
      offer: getIndividualOfferFactory({ lastProvider: { name: 'allociné' } }),
    })

    expect(screen.getByLabelText('Prix par personne')).not.toBeDisabled()
  })

  it('should disabled field for provider', () => {
    renderPriceCategories({
      offer: getIndividualOfferFactory({
        lastProvider: { name: 'provider' },
      }),
    })

    expect(screen.getByLabelText('Prix par personne')).toBeDisabled()
  })

  it('should disabled field for pending offer', () => {
    renderPriceCategories({
      offer: getIndividualOfferFactory({ status: OfferStatus.PENDING }),
    })

    expect(screen.getByLabelText('Prix par personne')).toBeDisabled()
  })

  it('should disabled field for rejected offer', () => {
    renderPriceCategories({
      offer: getIndividualOfferFactory({ status: OfferStatus.REJECTED }),
    })

    expect(screen.getByLabelText('Prix par personne')).toBeDisabled()
  })
})
