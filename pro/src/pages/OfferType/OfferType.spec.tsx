import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { OfferType } from '@/pages/OfferType/OfferType'

const renderOfferTypes = (initialRoute = '/') => {
  renderWithProviders(
    <Routes>
      <Route path="/" element={<OfferType />} />
      <Route path="/onboarding" element={<OfferType />} />
    </Routes>,
    {
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [initialRoute],
    }
  )
}

describe('OfferType', () => {
  it('should display with the lateral bar', () => {
    renderOfferTypes()
    expect(screen.getByTestId('lateral-panel')).toBeInTheDocument()
  })

  it('should not render when the offer is not set', () => {
    renderOfferTypes('/onboarding')
    expect(screen.queryByTestId('lateral-panel')).not.toBeInTheDocument()
  })

  it('should show a generic title if the url does not contain the collective type', () => {
    renderOfferTypes('/')
    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
  })

  it('should show a collective specific title if the url contains the collective type', () => {
    renderOfferTypes('/?type=collective')
    expect(
      screen.getByRole('heading', { name: 'Créer une offre collective' })
    ).toBeInTheDocument()
  })
})
