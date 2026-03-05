import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { IndividualOfferWizard } from '@/pages/IndividualOfferWizard/IndividualOfferWizard'

vi.mock('@/apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
  },
}))

const renderOffer = (initialRoute = '/') => {
  return renderWithProviders(
    <Routes>
      <Route path="/" element={<IndividualOfferWizard />} />
      <Route path="/onboarding" element={<IndividualOfferWizard />} />
    </Routes>,
    { initialRouterEntries: [initialRoute] }
  )
}

describe('IndividualOfferWizard', () => {
  it('should display with the lateral bar', async () => {
    renderOffer()
    expect(await screen.findByTestId('lateral-panel')).toBeInTheDocument()
  })

  it('should not render when the offer is not set', () => {
    renderOffer('/onboarding')
    expect(screen.queryByTestId('lateral-panel')).not.toBeInTheDocument()
  })
})
