import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import StocksProviderFormContainer from 'components/pages/Venue/VenueEdition/VenueProvidersManager/StocksProviderForm/StocksProviderFormContainer'
import { configureTestStore } from 'store/testUtils'
import * as fetch from 'utils/fetch'

const renderStocksProviderForm = props => {
  const stubbedStore = configureTestStore({ notification: {} })

  render(
    <Provider store={stubbedStore}>
      <MemoryRouter>
        <StocksProviderFormContainer {...props} />
      </MemoryRouter>
    </Provider>
  )

  return stubbedStore
}

describe('src | StocksProviderForm', () => {
  let props

  beforeEach(() => {
    props = {
      cancelProviderSelection: jest.fn(),
      historyPush: jest.fn(),
      offererId: 'O1',
      providerId: 'P1',
      siret: '12345678901234',
      venueId: 'V1',
    }
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('at first', () => {
    it('should display an import button and the venue siret as provider identifier', () => {
      // when
      renderStocksProviderForm(props)

      // then
      expect(screen.queryByRole('button', { name: 'Importer' })).toBeInTheDocument()
      expect(screen.queryByText('Compte')).toBeInTheDocument()
      expect(screen.queryByText('12345678901234')).toBeInTheDocument()
    })
  })

  describe('when submit the form', () => {
    it('should display the spinner', async () => {
      // given
      renderStocksProviderForm(props)
      jest.spyOn(global, 'fetch').mockResolvedValue({
        json: () => Promise.resolve(),
        ok: true,
      })
      const submitButton = screen.getByRole('button', { name: 'Importer' })
      jest.spyOn(fetch, 'fetchFromApiWithCredentials').mockResolvedValue()

      // when
      await waitFor(() => fireEvent.click(submitButton))

      // then
      expect(screen.getByText('Vérification de votre rattachement')).toBeInTheDocument()
      expect(fetch.fetchFromApiWithCredentials).toHaveBeenCalledWith('/venueProviders', 'POST', {
        providerId: 'P1',
        venueId: 'V1',
        venueIdAtOfferProvider: '12345678901234',
      })
    })

    it('should display the venue page if the venue provider is created', async () => {
      // given
      renderStocksProviderForm(props)
      jest.spyOn(global, 'fetch').mockResolvedValue({
        json: () => Promise.resolve(),
        ok: true,
        status: 201,
      })
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await waitFor(() => fireEvent.click(submitButton))

      // then
      expect(props.historyPush).toHaveBeenCalledWith('/structures/O1/lieux/V1')
    })

    it('should display a notification if there is something wrong with the server', async () => {
      // given
      const stubbedStore = renderStocksProviderForm(props)
      jest.spyOn(global, 'fetch').mockResolvedValue({
        json: () => Promise.resolve({ errors: ['error message'] }),
        ok: false,
      })
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await waitFor(() => fireEvent.click(submitButton))

      // then
      expect(props.cancelProviderSelection).toHaveBeenCalledTimes(1)
      expect(stubbedStore.getState().notification).toStrictEqual({
        text: 'error message',
        type: 'danger',
        version: 1,
      })
    })
  })
})
