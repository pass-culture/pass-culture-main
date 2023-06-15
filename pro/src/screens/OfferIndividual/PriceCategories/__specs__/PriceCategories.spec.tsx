import { screen } from '@testing-library/react'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PriceCategories, { IPriceCategories } from '../PriceCategories'

const renderPriceCategories = (props: IPriceCategories) =>
  renderWithProviders(<PriceCategories {...props} />)

describe('PriceCategories', () => {
  it('should render without error', () => {
    renderPriceCategories({ offer: individualOfferFactory() })

    expect(screen.getByText('Tarifs')).toBeInTheDocument()
  })

  it('should render provider banner', () => {
    renderPriceCategories({
      offer: individualOfferFactory({ lastProviderName: 'allociné' }),
    })

    expect(
      screen.getByText('Offre synchronisée avec Allociné')
    ).toBeInTheDocument()
  })

  it('should not disabled field for allociné', () => {
    renderPriceCategories({
      offer: individualOfferFactory({ lastProviderName: 'allociné' }),
    })

    expect(screen.getByLabelText('Prix par personne')).not.toBeDisabled()
  })

  it('should disabled field for provider', () => {
    renderPriceCategories({
      offer: individualOfferFactory({
        lastProvider: {
          name: 'provider',
        },
        lastProviderName: 'provider',
      }),
    })

    expect(screen.getByLabelText('Prix par personne')).toBeDisabled()
  })

  it('should disabled field for pending offer', () => {
    renderPriceCategories({
      offer: individualOfferFactory({ status: OfferStatus.PENDING }),
    })

    expect(screen.getByLabelText('Prix par personne')).toBeDisabled()
  })

  it('should disabled field for rejected offer', () => {
    renderPriceCategories({
      offer: individualOfferFactory({ status: OfferStatus.REJECTED }),
    })

    expect(screen.getByLabelText('Prix par personne')).toBeDisabled()
  })
})
