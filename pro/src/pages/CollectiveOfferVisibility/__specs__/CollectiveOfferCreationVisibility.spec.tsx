import { screen } from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferCreationVisibility, {
  CollectiveOfferVisibilityProps,
} from '../CollectiveOfferCreationVisibility'

jest.mock('apiClient/api', () => ({
  api: {
    getEducationalInstitutions: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: jest.fn(),
}))

const renderCollectiveOfferCreationVisibility = (
  path: string,
  props: CollectiveOfferVisibilityProps
) => {
  renderWithProviders(<CollectiveOfferCreationVisibility {...props} />, {
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: jest.fn(),
}

describe('CollectiveOfferCreationVisibility', () => {
  it('should render collective offer visibility form', async () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'A1' })
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
