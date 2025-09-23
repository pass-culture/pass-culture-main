import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { COLLECTIVE_OFFER_CREATION_TITLE } from '@/components/CollectiveBudgetInformation/constants'
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
        user: { currentUser: sharedCurrentUserFactory() },
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

  it('should render the collective budget information when not onboarding and offerer is allowed on adage', async () => {
    renderOfferTypes('/?type=collective', true)

    expect(
      await screen.findByText(COLLECTIVE_OFFER_CREATION_TITLE)
    ).toBeInTheDocument()
  })

  it('should not render the collective budget information when not onboarding and offerer is not allowed on adage', async () => {
    renderOfferTypes('/?type=collective', false)

    await waitFor(() => {
      expect(
        screen.queryByText(COLLECTIVE_OFFER_CREATION_TITLE)
      ).not.toBeInTheDocument()
    })
  })
})
