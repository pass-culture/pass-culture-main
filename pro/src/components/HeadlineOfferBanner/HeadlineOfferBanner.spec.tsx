import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import * as useAnalytics from 'app/App/analytics/firebase'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { HeadlineOfferBanner } from './HeadlineOfferBanner'

const renderHeadlineOfferBaner = () => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/"
        element={<HeadlineOfferBanner />}
      />
    </Routes>
  )
}

describe('HeadlineOfferBanner', () => {
  it('should open offer headline dialog when clicking on "Découvrir"', async () => {
    renderHeadlineOfferBaner()

    await userEvent.click(screen.getByText(/Découvrir/))

    expect(
      screen.getByText(/Nouvelle fonctionnalité : la mise à la une !/)
    ).toBeInTheDocument()
  })

  it('should render awesome banner when user is in ab test', () => {
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      PRO_EXPERIMENT_GTM_HEADLINE_OFFER: 'true',
    })

    renderHeadlineOfferBaner()

    expect(screen.getByTestId('awesome-banner')).toBeInTheDocument()
  })

  it('should render regular banner when user is not in ab test', () => {
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      PRO_EXPERIMENT_GTM_HEADLINE_OFFER: 'false',
    })

    renderHeadlineOfferBaner()

    expect(screen.getByTestId('regular-banner')).toBeInTheDocument()
  })
})
