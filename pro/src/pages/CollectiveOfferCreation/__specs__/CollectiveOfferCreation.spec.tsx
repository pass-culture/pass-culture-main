import { screen } from '@testing-library/react'
import React from 'react'

import { OptionalCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferCreation } from '../CollectiveOfferCreation'

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
    listEducationalDomains: vi.fn(),
    listEducationalOfferers: vi.fn(),
    canOffererCreateEducationalOffer: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

const renderCollectiveOfferCreation = (
  path: string,
  props: OptionalCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferCreation {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      features: {
        list: [{ isActive: true, name: 'WIP_ENABLE_NATIONAL_SYSTEM' }],
      },
    },
  })
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: vi.fn(),
  reloadCollectiveOffer: vi.fn(),
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
