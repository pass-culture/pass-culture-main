import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from 'utils/stubStore'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import Desk from '../Desk'

const renderDesk = props => {
  const stubbedStore = getStubStore({
    data: (
      state = {
        users: [{ publicName: 'USER' }],
        offerers: [{}],
      }
    ) => state,
    modal: (
      state = {
        config: {},
      }
    ) => state,
  })

  render(
    <Provider store={stubbedStore}>
      <MemoryRouter>
        <Desk {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('src | components | Desk', () => {
  let props

  beforeEach(() => {
    props = {
      getBooking: jest.fn(),
      trackValidateBookingSuccess: jest.fn(),
      validateBooking: jest.fn(),
    }
  })

  it('should display a title, a description and a text input', () => {
    // when
    renderDesk(props)

    // then
    const title = screen.getByText('Guichet', { selector: 'h1' })
    expect(title).toBeInTheDocument()
    const description = screen.getByText(
      'Enregistrez les contremarques de réservations présentés par les porteurs du pass.'
    )
    expect(description).toBeInTheDocument()
    const input = screen.getByPlaceholderText('ex : AZE123')
    expect(input).toHaveAttribute('maxLength', '6')
    expect(input).toHaveAttribute('type', 'text')
    const bookingUser = queryByTextTrimHtml(screen, 'Utilisateur : Fake user name')
    expect(bookingUser).not.toBeInTheDocument()
    const bookingOffer = queryByTextTrimHtml(screen, 'Offre : Fake offer')
    expect(bookingOffer).not.toBeInTheDocument()
    const bookingDate = queryByTextTrimHtml(screen, 'Date de l’offre : Permanent')
    expect(bookingDate).not.toBeInTheDocument()
    const bookingPrice = queryByTextTrimHtml(screen, 'Prix : 40 €')
    expect(bookingPrice).not.toBeInTheDocument()
  })

  describe('while the token is not correctly filled', () => {
    it('should display a message when input is empty', () => {
      // given
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: '' } })

      // then
      expect(screen.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
      expect(screen.getByText('Saisissez une contremarque')).toBeInTheDocument()
    })

    it('should display a message while the user is typing a token', () => {
      // given
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'ABCDE' } })

      // then
      expect(screen.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
      expect(screen.getByText('Caractères restants : 1/6')).toBeInTheDocument()
    })

    it('should display a message when token is invalid', () => {
      // given
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'ù^`@' } })

      // then
      expect(screen.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
      expect(screen.getByText('Caractères valides : de A à Z et de 0 à 9')).toBeInTheDocument()
    })
  })

  describe('when the input field is filled with a valid token', () => {
    it('should display a message and booking informations', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockImplementation(() =>
        Promise.resolve({
          datetime: null,
          offerName: 'Fake offer',
          userName: 'Fake user name',
          price: 40,
        })
      )
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })

      // then
      expect(screen.getByText('Vérification...')).toBeInTheDocument()
      const submitButton = await screen.findByRole('button', { name: 'Valider la contremarque' })
      expect(submitButton).toBeEnabled()
      const responseFromApi = await screen.findByText(
        'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
      )
      expect(responseFromApi).toBeInTheDocument()
      const bookingUser = await queryByTextTrimHtml(screen, 'Utilisateur : Fake user name')
      expect(bookingUser).toBeInTheDocument()
      const bookingOffer = await queryByTextTrimHtml(screen, 'Offre : Fake offer')
      expect(bookingOffer).toBeInTheDocument()
      const bookingDate = await queryByTextTrimHtml(screen, 'Date de l’offre : Permanent')
      expect(bookingDate).toBeInTheDocument()
      const bookingPrice = await queryByTextTrimHtml(screen, 'Prix : 40 €')
      expect(bookingPrice).toBeInTheDocument()
    })

    it('should display an error message when token validation fails', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockImplementation(() =>
        Promise.reject({
          json: jest.fn(() => Promise.resolve({ booking: 'token is used or invalid' })),
        })
      )
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })

      // then
      const errorMessage = await screen.findByText('token is used or invalid')
      expect(errorMessage).toBeInTheDocument()
    })
  })

  describe('when I can submit the form', () => {
    it('should display a message when booking is registered', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockImplementation(() => Promise.resolve({}))
      jest.spyOn(props, 'validateBooking').mockImplementation(() => Promise.resolve())
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')
      const submitButton = screen.getByRole('button', { name: 'Valider la contremarque' })
      await waitFor(() => fireEvent.change(tokenInput, { target: { value: 'MEFA01' } }))

      // when
      fireEvent.click(submitButton)

      // then
      expect(screen.getByText('Enregistrement en cours...')).toBeInTheDocument()
      const responseFromApi = await screen.findByText('Enregistrement réussi !')
      expect(responseFromApi).toBeInTheDocument()
    })

    it('should display an error message when the booking registration has failed', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockImplementation(() => Promise.resolve({}))
      jest
        .spyOn(props, 'validateBooking')
        .mockImplementation(() =>
          Promise.reject({ json: jest.fn(() => Promise.resolve({ booking: 'error message' })) })
        )
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')
      const submitButton = screen.getByRole('button', { name: 'Valider la contremarque' })
      await waitFor(() => fireEvent.change(tokenInput, { target: { value: 'MEFA01' } }))

      // when
      fireEvent.click(submitButton)

      // then
      const responseFromApi = await screen.findByText('error message')
      expect(responseFromApi).toBeInTheDocument()
    })
  })
})
