import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import {
  categoriesFactory,
  subCategoriesFactory,
} from 'screens/OfferEducational/__tests-utils__'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSummary, {
  CollectiveOfferSummaryProps,
} from '../CollectiveOfferSummary'

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getVenue: vi.fn(),
  },
}))

const renderCollectiveOfferSummary = (
  props: CollectiveOfferSummaryProps,
  storeOverride?: any
) => {
  renderWithProviders(<CollectiveOfferSummary {...props} />, {
    storeOverrides: storeOverride,
  })
}

describe('CollectiveOfferSummary', () => {
  let props: CollectiveOfferSummaryProps
  beforeEach(() => {
    const offer = collectiveOfferFactory()
    props = {
      offer,
      categories: {
        educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
        educationalSubCategories: subCategoriesFactory([
          { categoryId: 'CAT_1', id: 'SUBCAT_1' },
        ]),
      },
    }
  })
  it('should show banner if generate from publicApi', async () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })

    renderCollectiveOfferSummary({
      ...props,
      offer,
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByText(
        'Offre créée par votre outil de billetterie via l’API offres collectives'
      )
    ).toBeInTheDocument()
  })

  it('should not see edit button if offer from publicApi', async () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })

    renderCollectiveOfferSummary({
      ...props,
      offer,
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.queryAllByRole('link', { name: 'Modifier' })).toHaveLength(0)
  })
  it('should display national program if ff is active', async () => {
    renderCollectiveOfferSummary(props, {
      features: {
        initialized: true,
        list: [
          {
            isActive: true,
            nameKey: 'WIP_ENABLE_NATIONAL_SYSTEM',
          },
        ],
      },
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(screen.getByText('Dispositif national :')).toBeInTheDocument()
    expect(screen.getByText('Collège au cinéma')).toBeInTheDocument()
  })
})
