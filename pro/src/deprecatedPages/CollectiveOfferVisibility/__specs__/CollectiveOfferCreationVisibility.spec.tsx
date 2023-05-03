import { screen } from '@testing-library/react'
import React from 'react'

import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferVisibility } from '../CollectiveOfferCreationVisibility'

jest.mock('apiClient/api', () => ({
  api: {
    getEducationalInstitutions: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

const renderCollectiveOfferCreationVisibility = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferVisibility {...props} />, {
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: jest.fn(),
  reloadCollectiveOffer: jest.fn(),
  isTemplate: false,
}

describe('CollectiveOfferVisibility', () => {
  it('should render collective offer visibility form', async () => {
    renderCollectiveOfferCreationVisibility(
      '/offre/A1/collectif/visibilite',
      defaultProps
    )

    expect(
      await screen.findByRole('heading', {
        name: 'Créer une nouvelle offre collective',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Visibilité de l’offre',
      })
    ).toBeInTheDocument()
  })
})
