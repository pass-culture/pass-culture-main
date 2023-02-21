import { screen } from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferStockCreation from '..'
import { OfferEducationalStockCreationProps } from '../CollectiveOfferStockCreation'

jest.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: jest.fn(),
}))

const renderCollectiveStockCreation = (
  path: string,
  props: OfferEducationalStockCreationProps
) => {
  renderWithProviders(<CollectiveOfferStockCreation {...props} />, {
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: jest.fn(),
}

describe('CollectiveOfferStockCreation', () => {
  it('should render collective offer stock form', async () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'A1' })
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', defaultProps)

    expect(
      await screen.findByRole('heading', {
        name: 'Créer une nouvelle offre collective',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Date et prix',
      })
    ).toBeInTheDocument()
  })
})
