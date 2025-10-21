import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import { OfferHighlightBanner } from '../OfferHighlightBanner'

vi.mock('@/apiClient/api', () => ({
  api: {
    getHighlights: vi.fn(),
  },
}))

function renderOfferHighlightBanner(props: { offerId: number }) {
  return renderWithProviders(
    <>
      <OfferHighlightBanner {...props} />
      <Notification />
    </>
  )
}

describe('OfferHighlightBanner', () => {
  it('should display the banner with text and button', () => {
    // When
    renderOfferHighlightBanner({ offerId: 1 })

    // Then
    expect(
      screen.getByText(
        'Valorisez votre évènement en l’associant à un temps fort.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Choisir un temps fort' })
    ).toBeInTheDocument()
  })

  it('should open the modal when clicking the button', async () => {
    // Given
    vi.spyOn(api, 'getHighlights').mockResolvedValueOnce([])

    // When
    renderOfferHighlightBanner({ offerId: 1 })
    await userEvent.click(
      screen.getByRole('button', { name: 'Choisir un temps fort' })
    )

    // Then
    expect(
      screen.getByRole('heading', { name: 'Choisir un temps fort' })
    ).toBeInTheDocument()
  })
})
