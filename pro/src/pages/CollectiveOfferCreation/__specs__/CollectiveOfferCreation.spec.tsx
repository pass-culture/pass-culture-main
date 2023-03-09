import { screen } from '@testing-library/react'
import React from 'react'

import { OptionalCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferCreation } from '../CollectiveOfferCreation'

jest.mock('apiClient/api', () => ({
  api: {
    getCategories: jest.fn(),
    listEducationalDomains: jest.fn(),
    listEducationalOfferers: jest.fn(),
    canOffererCreateEducationalOffer: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

const renderCollectiveOfferCreation = (
  path: string,
  props: OptionalCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferCreation {...props} />, {
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: jest.fn(),
  reloadCollectiveOffer: jest.fn(),
  isTemplate: false,
}

describe('CollectiveOfferCreation', () => {
  it('should render collective offer creation form', async () => {
    renderCollectiveOfferCreation('/offre/creation/collectif', defaultProps)

    expect(
      await screen.findByRole('heading', {
        name: 'Créer une nouvelle offre collective',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Lieu de rattachement de votre offre',
      })
    ).toBeInTheDocument()
  })

  it('should render with template tag', async () => {
    renderCollectiveOfferCreation('/offre/creation/collectif/vitrine', {
      ...defaultProps,
      isTemplate: true,
    })

    expect(
      await screen.findByRole('heading', {
        name: 'Créer une nouvelle offre collective',
      })
    ).toBeInTheDocument()
    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
  })
})
