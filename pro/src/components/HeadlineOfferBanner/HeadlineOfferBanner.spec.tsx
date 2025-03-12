import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { HeadlineOfferBanner } from './HeadlineOfferBanner'

const renderHeadlineOfferBanner = (userId: number = 2) => {
  return renderWithProviders(<HeadlineOfferBanner />, {
    user: sharedCurrentUserFactory({ id: userId }),
  })
}

describe('HeadlineOfferBanner', () => {
  it('should open offer headline dialog when clicking on "Découvrir"', async () => {
    renderHeadlineOfferBanner(1)

    await userEvent.click(screen.getByText(/Découvrir/))

    expect(
      screen.getByText(/Nouvelle fonctionnalité : la mise à la une !/)
    ).toBeInTheDocument()
  })

  it('should render awesome banner when user is in ab test', () => {
    renderHeadlineOfferBanner(2)

    expect(screen.getByTestId('awesome-banner')).toBeInTheDocument()
  })

  it('should render regular banner when user is not in ab test', () => {
    renderHeadlineOfferBanner(1)

    expect(screen.getByTestId('regular-banner')).toBeInTheDocument()
  })
})
