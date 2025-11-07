import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { OfferType } from '@/pages/OfferType/OfferType'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
  },
}))

const renderOfferTypes = (initialRoute = '/', allowedOnAdage = false) => {
  renderWithProviders(
    <Routes>
      <Route path="/" element={<OfferType />} />
      <Route path="/onboarding" element={<OfferType />} />
    </Routes>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
        offerer: { currentOfferer: { allowedOnAdage } },
      },
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [initialRoute],
    }
  )
}

describe('OfferType', () => {
  it('should display with the lateral bar', async () => {
    renderOfferTypes()
    expect(await screen.findByTestId('lateral-panel')).toBeInTheDocument()
  })

  it('should not render when the offer is not set', async () => {
    renderOfferTypes('/onboarding')
    await waitFor(() => {
      expect(screen.queryByTestId('lateral-panel')).not.toBeInTheDocument()
    })
  })

  it('should show a generic title if the url does not contain the collective type', async () => {
    renderOfferTypes('/')
    expect(
      await screen.findByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
  })

  it('should show a collective specific title if the url contains the collective type', async () => {
    renderOfferTypes('/?type=collective')
    expect(
      await screen.findByRole('heading', { name: 'Créer une offre collective' })
    ).toBeInTheDocument()
  })
})
