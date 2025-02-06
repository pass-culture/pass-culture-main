import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { HeadlineOfferBanner } from './HeadlineOfferBanner'

const renderHeadlineOfferBaner = () => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/"
        element={<HeadlineOfferBanner close={() => {}}/>}
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
})
