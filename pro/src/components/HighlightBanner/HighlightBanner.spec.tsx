import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import * as storageAvailable from '@/commons/utils/storageAvailable'

import { HighlightBanner } from './HighlightBanner'

describe('HighlightBanner', () => {
  it('should close highlight banner', async () => {
    renderWithProviders(
      <HighlightBanner
        title="test title"
        description="test 123"
        localStorageKey="TEST_LOCAL_KEY"
      />
    )

    screen.getByText('test title')

    const closeButton = screen.getByRole('button', {
      name: 'Fermer la bannière',
    })

    await userEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByText('test title')).not.toBeInTheDocument()
    })
  })

  it('should not display highlight banner if the localstorage is not available', () => {
    vi.spyOn(storageAvailable, 'storageAvailable').mockImplementationOnce(
      () => false
    )

    renderWithProviders(
      <HighlightBanner
        title="test title"
        description="test 123"
        localStorageKey="TEST_LOCAL_KEY"
      />
    )

    expect(screen.queryByText('test title')).not.toBeInTheDocument()
  })
})
