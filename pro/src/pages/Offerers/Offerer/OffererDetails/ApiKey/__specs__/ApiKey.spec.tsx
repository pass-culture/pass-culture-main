import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import * as notificationReducer from 'store/notifications/reducer'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ApiKey } from '../ApiKey'

const defaultProps = {
  maxAllowedApiKeys: 5,
  savedApiKeys: ['key-prefix1'],
  reloadOfferer: vi.fn(),
}
const offererId = 1

Object.assign(navigator, {
  clipboard: {
    writeText: () => {},
  },
})

const renderApiKey = (props = defaultProps) =>
  renderWithProviders(
    <ApiKey
      maxAllowedApiKeys={props.maxAllowedApiKeys}
      offererId={offererId}
      reloadOfferer={props.reloadOfferer}
      savedApiKeys={props.savedApiKeys}
    />
  )

Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: () => {},
  },
})

describe('ApiKey', () => {
  it('should display api keys and generate new key', () => {
    renderApiKey()

    expect(screen.getByText('key-prefix1********')).toBeInTheDocument()
    expect(screen.getByText('1/5')).toBeInTheDocument()
  })

  it('should display the button as disabled if limit reached', () => {
    renderApiKey({
      maxAllowedApiKeys: 5,
      savedApiKeys: ['key1', 'key2', 'key3', 'key4', 'key5'],
      reloadOfferer: defaultProps.reloadOfferer,
    })

    expect(screen.getByText('Générer une clé API')).toBeDisabled()
  })

  it('should generate a new key', async () => {
    renderApiKey()
    vi.spyOn(api, 'generateApiKeyRoute').mockResolvedValue({
      apiKey: 'new-key',
    })

    await userEvent.click(screen.getByText('Générer une clé API'))

    expect(screen.getByText('new-key')).toBeInTheDocument()
  })

  it('should copy key in clipboar', async () => {
    renderApiKey()
    vi.spyOn(navigator.clipboard, 'writeText')
    vi.spyOn(api, 'generateApiKeyRoute').mockResolvedValue({
      apiKey: 'new-key',
    })
    await userEvent.click(screen.getByText('Générer une clé API'))
    screen.getByText('Copier')

    await userEvent.click(screen.getByText('Copier'))

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('new-key')
  })

  it('should display an error when the api call fails', async () => {
    renderApiKey()

    const showNotificationSpy = vi.spyOn(
      notificationReducer,
      'showNotification'
    )
    vi.spyOn(api, 'generateApiKeyRoute').mockRejectedValue(null)

    await userEvent.click(screen.getByText('Générer une clé API'))

    expect(showNotificationSpy).toHaveBeenCalledWith({
      type: 'error',
      duration: 5000,
      text: 'Une erreur s’est produite, veuillez réessayer',
    })
  })

  it('should not delete key on modal dismiss', async () => {
    renderApiKey()
    const deleteSpy = vi.spyOn(api, 'deleteApiKey').mockResolvedValue()
    await userEvent.click(screen.getByText('supprimer'))

    await userEvent.click(screen.getByText('Annuler'))

    expect(deleteSpy).not.toHaveBeenCalled()
    expect(defaultProps.reloadOfferer).not.toHaveBeenCalledWith()
  })

  it('should delete a key on modal confirm', async () => {
    renderApiKey()
    const deleteSpy = vi.spyOn(api, 'deleteApiKey').mockResolvedValue()
    await userEvent.click(screen.getByText('supprimer'))

    await userEvent.click(screen.getByText('Confirmer la suppression'))

    expect(deleteSpy).toHaveBeenCalledWith('key-prefix1')
    expect(defaultProps.reloadOfferer).toHaveBeenCalledWith(offererId)
  })

  it('should not replace savedApiKeys by new one when creating and directly deleting previous one', async () => {
    renderApiKey({
      maxAllowedApiKeys: 5,
      savedApiKeys: ['old-key'],
      reloadOfferer: defaultProps.reloadOfferer,
    })
    vi.spyOn(api, 'generateApiKeyRoute').mockResolvedValueOnce({
      apiKey: 'new-key',
    })
    vi.spyOn(api, 'deleteApiKey').mockResolvedValueOnce()

    expect(screen.getByText('old-key********')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Générer une clé API'))

    await userEvent.click(screen.getByText('supprimer'))
    await userEvent.click(screen.getByText('Confirmer la suppression'))

    expect(screen.queryByText('new-key********')).not.toBeInTheDocument()
    expect(screen.getByText('new-key')).toBeInTheDocument()
  })
})
