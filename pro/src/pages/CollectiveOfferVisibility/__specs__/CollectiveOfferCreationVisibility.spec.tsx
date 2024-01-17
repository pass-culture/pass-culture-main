import { screen } from '@testing-library/react'
import React from 'react'

import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferVisibility } from '../CollectiveOfferCreationVisibility'

vi.mock('apiClient/api', () => ({
  api: {
    getEducationalInstitutions: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

const renderCollectiveOfferCreationVisibility = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  storeOverride?: any
) => {
  renderWithProviders(<CollectiveOfferVisibility {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: storeOverride,
  })
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: vi.fn(),
  reloadCollectiveOffer: vi.fn(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferVisibility', () => {
  it('should render collective offer visibility form', async () => {
    renderCollectiveOfferCreationVisibility(
      '/offre/A1/collectif/visibilite',
      defaultProps
    )

    expect(
      await screen.findByRole('heading', {
        name: /Créer une nouvelle offre collective/,
      })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', {
        name: 'Établissement scolaire et enseignant',
      })
    ).toBeInTheDocument()
  })
  it('should render new collective offer visibility form if ff active', async () => {
    renderCollectiveOfferCreationVisibility(
      '/offre/A1/collectif/visibilite',
      defaultProps
    )

    expect(
      await screen.findByRole('heading', {
        name: 'Établissement scolaire et enseignant',
      })
    ).toBeInTheDocument()
  })
})
