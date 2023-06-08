import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import * as notificationReducer from 'store/reducers/notificationReducer'
import {
  failToGenerateOffererApiKey,
  generateFakeOffererApiKey,
} from 'utils/fakeApi'
import { renderWithProviders } from 'utils/renderWithProviders'

import ApiKey from '../ApiKey'

const defaultProps = {
  maxAllowedApiKeys: 5,
  savedApiKeys: ['key-prefix1'],
  reloadOfferer: jest.fn(),
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
    // when
    renderApiKey()

    // then
    expect(screen.getByText('key-prefix1********')).toBeInTheDocument()
    expect(screen.getByText('1/5')).toBeInTheDocument()
  })

  it('should display the button as disabled if limit reached', () => {
    // when
    renderApiKey({
      maxAllowedApiKeys: 5,
      savedApiKeys: ['key1', 'key2', 'key3', 'key4', 'key5'],
      reloadOfferer: defaultProps.reloadOfferer,
    })

    // then
    expect(
      screen.getByText('Générer une clé API', { selector: 'button' })
    ).toBeDisabled()
  })

  it('should generate a new key', async () => {
    // given
    renderApiKey()
    generateFakeOffererApiKey('new-key')

    // when
    await userEvent.click(
      screen.getByText('Générer une clé API', { selector: 'button' })
    )

    // then
    expect(screen.getByText('new-key')).toBeInTheDocument()
  })

  it('should copy key in clipboar', async () => {
    // given
    renderApiKey()
    jest.spyOn(navigator.clipboard, 'writeText')
    generateFakeOffererApiKey('new-key')
    await userEvent.click(
      screen.getByText('Générer une clé API', { selector: 'button' })
    )
    screen.getByText('Copier', { selector: 'button' })

    // when
    await userEvent.click(screen.getByText('Copier', { selector: 'button' }))

    // then
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('new-key')
  })

  it('should display an error when the api call fails', async () => {
    // given
    renderApiKey()

    const showNotificationSpy = jest.spyOn(
      notificationReducer,
      'showNotification'
    )
    failToGenerateOffererApiKey()

    // when
    await userEvent.click(
      screen.getByText('Générer une clé API', { selector: 'button' })
    )

    // then
    expect(showNotificationSpy).toHaveBeenCalledWith({
      type: 'error',
      duration: 5000,
      text: "Une erreur s'est produite, veuillez réessayer",
    })
  })

  it('should not delete key on modal dismiss', async () => {
    renderApiKey()
    const deleteSpy = jest.spyOn(api, 'deleteApiKey').mockResolvedValue()
    await userEvent.click(screen.getByText('supprimer'))

    // when
    await userEvent.click(screen.getByText('Annuler', { selector: 'button' }))

    // then
    expect(deleteSpy).not.toHaveBeenCalled()

    expect(defaultProps.reloadOfferer).not.toHaveBeenCalledWith()
  })

  it('should delete a key on modal confirm', async () => {
    renderApiKey()
    const deleteSpy = jest.spyOn(api, 'deleteApiKey').mockResolvedValue()
    await userEvent.click(screen.getByText('supprimer'))

    // when
    await userEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    // then
    expect(deleteSpy).toHaveBeenCalledWith('key-prefix1')
    expect(defaultProps.reloadOfferer).toHaveBeenCalledWith(offererId)
  })
})
