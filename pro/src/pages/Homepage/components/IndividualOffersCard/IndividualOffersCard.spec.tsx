import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { defaultOfferHomeResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OffersCardVariant } from '../types'
import { IndividualOffersCard } from './IndividualOffersCard'

vi.mock('@/apiClient/api', () => ({ api: { listOffersHome: vi.fn() } }))
vi.mock('../OffersRetentionCard/OffersRetentionCard', () => ({
  OffersRetentionCard: () => <div>OffersRetentionCard</div>,
}))

const mockLogEvent = vi.fn()

describe('<IndividualOffersCard />', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })
  it('should render without accessibility violations', async () => {
    vi.spyOn(api, 'listOffersHome').mockResolvedValueOnce([
      defaultOfferHomeResponseModel,
    ])
    const { container } = renderWithProviders(
      <IndividualOffersCard venueId={12} venueDepartmentCode={'75'} />
    )

    // waitFor allows to wait for the complete render of the component (after the request response)
    await waitFor(async () => {
      expect(await axe(container)).toHaveNoViolations()
    })
  })

  it('should render the retention card if no offers are returned', async () => {
    vi.spyOn(api, 'listOffersHome').mockResolvedValueOnce([])
    renderWithProviders(
      <IndividualOffersCard venueId={12} venueDepartmentCode={'75'} />
    )
    expect(await screen.findByText('OffersRetentionCard')).toBeVisible()
  })

  it('should have a CTA that sends to individual offer list', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'listOffersHome').mockResolvedValueOnce([
      defaultOfferHomeResponseModel,
    ])

    renderWithProviders(null, {
      routes: [
        {
          path: '/',
          element: (
            <IndividualOffersCard venueId={12} venueDepartmentCode={'75'} />
          ),
        },
        {
          path: '/offres',
          element: <div>Liste de toutes les offres individuelles</div>,
        },
      ],
    })

    const allOffersBtn = await screen.findByRole('link', {
      name: 'Voir toutes les offres',
    })
    expect(allOffersBtn).toBeVisible()
    await user.click(allOffersBtn)

    expect(
      screen.getByText('Liste de toutes les offres individuelles')
    ).toBeVisible()
  })

  it('should log event on press CTA that sends to individual offer list', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'listOffersHome').mockResolvedValueOnce([
      defaultOfferHomeResponseModel,
    ])

    renderWithProviders(
      <IndividualOffersCard venueId={12} venueDepartmentCode={'75'} />
    )

    const allOffersBtn = await screen.findByRole('link', {
      name: 'Voir toutes les offres',
    })
    expect(allOffersBtn).toBeVisible()
    await user.click(allOffersBtn)

    expect(mockLogEvent).toHaveBeenCalledWith(
      HomepageEvents.CLICKED_SEE_ALL_OFFERS,
      {
        offersVariant: OffersCardVariant.INDIVIDUAL,
        hasOffersDisplayed: true,
      }
    )
  })
})
