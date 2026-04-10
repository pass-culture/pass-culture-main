import { waitFor } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { defaultOfferHomeResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOffersCard } from './IndividualOffersCard'

vi.mock('@/apiClient/api', () => ({ api: { listOffersHome: vi.fn() } }))

describe('<IndividualOffersCard />', () => {
  it('should render without accessibility violations', async () => {
    vi.spyOn(api, 'listOffersHome').mockResolvedValue([
      defaultOfferHomeResponseModel,
    ])
    const { container } = renderWithProviders(
      <IndividualOffersCard venueId={12} venueDepartement={'75'} />
    )

    // waitFor allows to wait for the complete render of the component (after the request response)
    await waitFor(async () => {
      expect(await axe(container)).toHaveNoViolations()
    })
  })
})
