import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import * as storageAvailable from '@/commons/utils/storageAvailable'

import { HighlightBanner } from './HighlightBanner'

describe('HighlightBanner', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should close highlight banner', async () => {
    renderWithProviders(
      <HighlightBanner
        title="test title"
        description="test 123"
        localStorageKey={LOCAL_STORAGE_KEY.DIFFUSE_HELP_ADAGE_SEEN}
      />
    )

    screen.getByText('test title')

    const closeButton = screen.getByRole('button', {
      name: 'Masquer le bandeau',
    })

    await userEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByText('test title')).not.toBeInTheDocument()
    })
    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.DIFFUSE_HELP_ADAGE_SEEN)
    ).toBe('true')
  })

  it('should not display highlight banner if it was already closed', () => {
    localStorage.setItem(LOCAL_STORAGE_KEY.DIFFUSE_HELP_ADAGE_SEEN, 'true')

    renderWithProviders(
      <HighlightBanner
        title="test title"
        description="test 123"
        localStorageKey={LOCAL_STORAGE_KEY.DIFFUSE_HELP_ADAGE_SEEN}
      />
    )

    expect(screen.queryByText('test title')).not.toBeInTheDocument()
  })

  it('should not display highlight banner if the localstorage is not available', () => {
    vi.spyOn(storageAvailable, 'storageAvailable').mockImplementationOnce(
      () => false
    )

    renderWithProviders(
      <HighlightBanner
        title="test title"
        description="test 123"
        localStorageKey={LOCAL_STORAGE_KEY.DIFFUSE_HELP_ADAGE_SEEN}
      />
    )

    expect(screen.queryByText('test title')).not.toBeInTheDocument()
  })
})
