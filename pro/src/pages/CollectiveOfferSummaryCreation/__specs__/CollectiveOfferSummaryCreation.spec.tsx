import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSummaryCreation, {
  CollectiveOfferSummaryCreationProps,
} from '../CollectiveOfferSummaryCreation'

jest.mock('apiClient/api', () => ({
  api: {
    getCategories: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: jest.fn(),
}))

const renderCollectiveOfferSummaryCreation = async (
  path: string,
  props: CollectiveOfferSummaryCreationProps
) => {
  renderWithProviders(<CollectiveOfferSummaryCreation {...props} />, {
    initialRouterEntries: [path],
  })
  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: jest.fn(),
}

describe('CollectiveOfferSummaryCreation', () => {
  it('should render collective offer summary ', async () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'A1' })
    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({ categories: [], subcategories: [] })
    await renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )
    expect(
      screen.getByRole('heading', {
        name: 'Créer une nouvelle offre collective',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Détails de l’offre',
      })
    ).toBeInTheDocument()
  })
})
