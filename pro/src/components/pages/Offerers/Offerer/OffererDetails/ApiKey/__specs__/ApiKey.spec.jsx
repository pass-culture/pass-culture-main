import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { api } from 'apiClient/api'
import * as pcapi from 'repository/pcapi/pcapi'
import * as notificationReducer from 'store/reducers/notificationReducer'
import { configureTestStore } from 'store/testUtils'
import {
  failToGenerateOffererApiKey,
  generateFakeOffererApiKey,
} from 'utils/fakeApi'

import ApiKey from '../ApiKey'

const store = configureTestStore()
const defaultProps = {
  maxAllowedApiKeys: 5,
  savedApiKeys: ['key-prefix1'],
  reloadOfferer: jest.fn(),
}

Object.assign(navigator, {
  clipboard: {
    writeText: () => {},
  },
})

const renderApiKey = async (props = defaultProps) => {
  return render(
    <Provider store={store}>
      <ApiKey
        maxAllowedApiKeys={props.maxAllowedApiKeys}
        offererId="AE"
        reloadOfferer={props.reloadOfferer}
        savedApiKeys={props.savedApiKeys}
      />
    </Provider>
  )
}

Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: () => {},
  },
})

describe('src | Offerer | ApiKey', () => {
  it('should display api keys and generate new key', async () => {
    // when
    await renderApiKey()

    // then
    expect(screen.getByText('key-prefix1********')).toBeInTheDocument()
    expect(screen.getByText('1/5')).toBeInTheDocument()
  })

  it('should display the button as disabled if limit reached', async () => {
    // when
    await renderApiKey({
      maxAllowedApiKeys: 5,
      savedApiKeys: ['key1', 'key2', 'key3', 'key4', 'key5'],
    })

    // then
    expect(
      screen.getByText('Générer une clé API', { selector: 'button' })
    ).toBeDisabled()
  })

  it('should generate a new key', async () => {
    // given
    await renderApiKey()
    generateFakeOffererApiKey('new-key')

    // when
    fireEvent.click(
      screen.getByText('Générer une clé API', { selector: 'button' })
    )

    // then
    await waitFor(() => expect(screen.getByText('new-key')).toBeInTheDocument())
  })

  it('should copy key in clipboar', async () => {
    // given
    await renderApiKey()
    jest.spyOn(navigator.clipboard, 'writeText')
    generateFakeOffererApiKey('new-key')
    fireEvent.click(
      screen.getByText('Générer une clé API', { selector: 'button' })
    )
    await waitFor(() => screen.getByText('Copier', { selector: 'button' }))

    // when
    fireEvent.click(screen.getByText('Copier', { selector: 'button' }))

    // then
    await waitFor(() =>
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('new-key')
    )
  })

  it('should display an error when the api call fails', async () => {
    // given
    await renderApiKey()

    const showNotificationSpy = jest.spyOn(
      notificationReducer,
      'showNotification'
    )
    failToGenerateOffererApiKey()

    // when
    fireEvent.click(
      screen.getByText('Générer une clé API', { selector: 'button' })
    )

    // then
    await waitFor(() =>
      expect(showNotificationSpy).toHaveBeenCalledWith({
        type: 'error',
        text: "Une erreur s'est produite, veuillez réessayer",
      })
    )
  })

  it('should not delete key on modal dismiss', async () => {
    await renderApiKey()
    const deleteSpy = jest.spyOn(api, 'deleteApiKey').mockReturnValue(null)
    fireEvent.click(screen.getByText('supprimer'))

    // when
    fireEvent.click(screen.getByText('Annuler', { selector: 'button' }))

    // then
    expect(deleteSpy).not.toHaveBeenCalled()
    await waitFor(() => {
      expect(defaultProps.reloadOfferer).not.toHaveBeenCalledWith()
    })
  })

  it('should delete a key on modal confirm', async () => {
    await renderApiKey()
    const deleteSpy = jest.spyOn(api, 'deleteApiKey').mockReturnValue(null)
    fireEvent.click(screen.getByText('supprimer'))

    // when
    fireEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    // then
    expect(deleteSpy).toHaveBeenCalledWith('key-prefix1')
    await waitFor(() => {
      expect(defaultProps.reloadOfferer).toHaveBeenCalledWith('AE')
    })
  })
})
