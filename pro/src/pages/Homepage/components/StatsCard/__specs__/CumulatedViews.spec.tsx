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
})
