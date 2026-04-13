import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { defaultOfferHomeResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOffersCard } from './IndividualOffersCard'

vi.mock('@/apiClient/api', () => ({ api: { listOffersHome: vi.fn() } }))
vi.mock('../OffersEmptyStateCard/OffersEmptyStateCard', () => ({
  OffersEmptyStateCard: () => <div>OffersEmptyStateCard</div>,
}))

describe('<IndividualOffersCard />', () => {
  it('should render without accessibility violations', async () => {
    vi.spyOn(api, 'listOffersHome').mockResolvedValue([
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

  it('should render the empty state if no offers are returned', async () => {
    vi.spyOn(api, 'listOffersHome').mockResolvedValue([])
    renderWithProviders(
      <IndividualOffersCard venueId={12} venueDepartmentCode={'75'} />
    )
    expect(await screen.findByText('OffersEmptyStateCard')).toBeVisible()
  })

  it('should have a CTA that sends to collective offer list', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'listOffersHome').mockResolvedValue([
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
})
