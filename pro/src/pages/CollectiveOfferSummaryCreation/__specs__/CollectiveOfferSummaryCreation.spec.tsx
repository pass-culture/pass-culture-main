import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import router from 'react-router-dom'

import { api } from 'apiClient/api'
import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferSummaryCreation } from '../CollectiveOfferSummaryCreation'

jest.mock('apiClient/api', () => ({
  api: {
    getCategories: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    requestId: jest.fn(),
  }),
}))

const renderCollectiveOfferSummaryCreation = async (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferSummaryCreation {...props} />, {
    initialRouterEntries: [path],
  })
  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: jest.fn(),
  reloadCollectiveOffer: jest.fn(),
  isTemplate: false,
}

describe('CollectiveOfferSummaryCreation', () => {
  it('should render collective offer summary ', async () => {
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

  it('should have requete parameter in the link for previous step when requete is present in the URL', async () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ requete: '1' })
    await renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )

    const previousStepLink = screen.getByText('Étape précédente')
    expect(previousStepLink.getAttribute('href')).toBe(
      '/offre/1/collectif/visibilite?requete=1'
    )
  })
})
