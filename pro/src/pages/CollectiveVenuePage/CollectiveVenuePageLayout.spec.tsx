import { screen } from '@testing-library/react'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveVenuePageLayout } from './CollectiveVenuePageLayout'

vi.mock(
  './components/PartnerPageCollectiveSection/PartnerPageCollectiveSection',
  () => ({
    PartnerPageCollectiveSection: () => (
      <div data-testid="partner-collective-section" />
    ),
  })
)

vi.mock('@/components/CollectiveDmsTimeline/CollectiveDmsTimeline', () => ({
  CollectiveDmsTimeline: () => <div data-testid="dms-timeline" />,
}))

const BANNER_TEXT = /Les informations suivantes sont visibles/

const renderCollectiveVenuePageLayout = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(null, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 7,
          ...venueOverrides,
        }),
      },
    },
    initialRouterEntries: ['/partenaire/page-collective'],
    routes: [
      {
        path: '/partenaire/page-collective',
        element: <CollectiveVenuePageLayout />,
        children: [{ index: true, element: <div>Outlet content</div> }],
      },
    ],
  })

describe('CollectiveVenuePageLayout', () => {
  it('should always display the collective section', () => {
    renderCollectiveVenuePageLayout()

    expect(screen.getByTestId('partner-collective-section')).toBeVisible()
  })

  it('should display the ADAGE banner and the outlet when active on ADAGE', () => {
    renderCollectiveVenuePageLayout({ hasAdageId: true, allowedOnAdage: true })

    expect(screen.getByText(BANNER_TEXT)).toBeVisible()
    expect(screen.getByText('Outlet content')).toBeVisible()
  })

  it('should not display the banner nor the outlet when not active on ADAGE', () => {
    renderCollectiveVenuePageLayout({ hasAdageId: false, allowedOnAdage: true })

    expect(screen.queryByText(BANNER_TEXT)).not.toBeInTheDocument()
    expect(screen.queryByText('Outlet content')).not.toBeInTheDocument()
  })

  it('should display the DMS timeline when a collective DMS application exists', () => {
    renderCollectiveVenuePageLayout({
      lastCollectiveDmsApplication: defaultDMSApplicationForEAC,
    })

    expect(screen.getByTestId('dms-timeline')).toBeVisible()
  })

  it('should not display the DMS timeline without a collective DMS application', () => {
    renderCollectiveVenuePageLayout({ lastCollectiveDmsApplication: null })

    expect(screen.queryByTestId('dms-timeline')).not.toBeInTheDocument()
  })
})
