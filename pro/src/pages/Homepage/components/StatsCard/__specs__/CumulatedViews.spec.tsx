import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event/dist/cjs/index.js'
import { venueOffersPeriodStatsModelFactory } from 'commons/utils/factories/statisticsFactories'
import {
  CumulatedViews,
  type CumulatedViewsProps,
} from 'pages/Homepage/components/StatsCard/components/CumulatedViews'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import type { VenueOffersPeriodStatsModel } from 'apiClient/v1'

const renderCumulatedViews = (props: CumulatedViewsProps) => {
  return renderWithProviders(<CumulatedViews {...props} />)
}

describe('CumulatedViews', () => {
  const periodStats: VenueOffersPeriodStatsModel =
    venueOffersPeriodStatsModelFactory()

  it('should render component', async () => {
    const { container } = renderCumulatedViews({ periodStats })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render table', async () => {
    renderCumulatedViews({ periodStats })

    await userEvent.click(screen.getByRole('tab', { name: 'Tableau' }))
    await waitFor(() => {
      expect(screen.getByText('octobre')).toBeInTheDocument()
    })
  })
})
