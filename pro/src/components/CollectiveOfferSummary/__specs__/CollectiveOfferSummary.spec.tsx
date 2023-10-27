import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { EacFormat } from 'apiClient/v1'
import {
  categoriesFactory,
  subCategoriesFactory,
} from 'screens/OfferEducational/__tests-utils__'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSummary, {
  CollectiveOfferSummaryProps,
} from '../CollectiveOfferSummary'
import { DEFAULT_RECAP_VALUE } from '../components/constants'

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getVenue: vi.fn(),
  },
}))

const isFormatActive = {
  features: {
    list: [
      {
        nameKey: 'WIP_ENABLE_FORMAT',
        isActive: true,
      },
    ],
    initialized: true,
  },
}

const renderCollectiveOfferSummary = (
  props: CollectiveOfferSummaryProps,
  storeOverrides?: any
) => {
  renderWithProviders(<CollectiveOfferSummary {...props} />, {
    storeOverrides: storeOverrides,
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
  it('should display national program', async () => {
    renderCollectiveOfferSummary(props)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(screen.getByText('Dispositif national :')).toBeInTheDocument()
    expect(screen.getByText('Collège au cinéma')).toBeInTheDocument()
  })
  it('should display format when ff is active', async () => {
    renderCollectiveOfferSummary(
      {
        ...props,
        offer: {
          ...props.offer,
          formats: [EacFormat.PROJECTION_AUDIOVISUELLE, EacFormat.CONCERT],
        },
      },
      isFormatActive
    )
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Format :')).toBeInTheDocument()
    expect(
      screen.getByText('Projection audiovisuelle, Concert')
    ).toBeInTheDocument()
  })

  it('should display defaut format value when null and ff is active', async () => {
    renderCollectiveOfferSummary(
      {
        ...props,
        offer: {
          ...props.offer,
          formats: null,
        },
      },
      isFormatActive
    )
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Format :')).toBeInTheDocument()
    expect(screen.getAllByText(DEFAULT_RECAP_VALUE)[0]).toBeInTheDocument()
  })

  it('should display the date and time if the FF is enabled', async () => {
    const offer = collectiveOfferTemplateFactory({
      dates: { start: '2023-10-24T09:14:00', end: '2023-10-24T09:16:00' },
    })
    renderCollectiveOfferSummary(
      { ...props, offer },
      {
        features: {
          list: [
            { isActive: true, nameKey: 'WIP_ENABLE_DATES_OFFER_TEMPLATE' },
          ],
        },
      }
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const title = screen.getByRole('heading', {
      name: 'Date et heure',
    })

    expect(title).toBeInTheDocument()
  })
})
