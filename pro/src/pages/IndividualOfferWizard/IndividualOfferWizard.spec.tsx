import { screen } from '@testing-library/react'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { IndividualOfferWizard } from 'pages/IndividualOfferWizard/IndividualOfferWizard'
import { Route, Routes } from 'react-router'

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
  it('should display with the lateral bar', () => {
    renderOffer()
    expect(screen.getByTestId('lateral-panel')).toBeInTheDocument()
  })

  it('should not render when the offer is not set', () => {
    renderOffer('/onboarding')
    expect(screen.queryByTestId('lateral-panel')).not.toBeInTheDocument()
  })
})
