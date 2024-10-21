import { screen } from '@testing-library/react'
import React from 'react'

import { getCollectiveOfferFactory } from 'commons/utils/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { MandatoryCollectiveOfferFromParamsProps } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

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
  offer: getCollectiveOfferFactory(),
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
