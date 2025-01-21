import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { HeadlineOfferBanner } from './HeadlineOfferBanner'

describe('HeadlineOfferBanner', () => {
  it('should open offer headline dialog when clicking on "Découvrir"', async () => {
    render(<HeadlineOfferBanner close={() => {}} />)

    await userEvent.click(screen.getByText(/Découvrir/))

    expect(
      screen.getByText(/Nouvelle fonctionnalité : la mise à la une !/)
    ).toBeInTheDocument()
  })
})
