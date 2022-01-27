/*
 * @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
 */

import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import Desk from '../Desk'

const renderDesk = props => {
  const store = configureTestStore({
    data: {
      users: [
        { publicName: 'USER', hasSeenProTutorials: true, isAdmin: false },
      ],
    },
  })

  render(
    <Provider store={store}>
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
      invalidateBooking: jest.fn(),
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
      'Saisissez les contremarques présentées par les bénéficiaires afin de les valider ou de les invalider.'
    )
    expect(description).toBeInTheDocument()
    const input = screen.getByPlaceholderText('ex : AZE123')
    expect(input).toHaveAttribute('type', 'text')
    const bookingUser = queryByTextTrimHtml(
      screen,
      'Utilisateur : Fake user name'
    )
    expect(bookingUser).not.toBeInTheDocument()
    const bookingOffer = queryByTextTrimHtml(screen, 'Offre : Fake offer')
    expect(bookingOffer).not.toBeInTheDocument()
    const bookingDate = queryByTextTrimHtml(
      screen,
      'Date de l’offre : Permanent'
    )
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
      expect(
        screen.getByRole('button', { name: 'Valider la contremarque' })
      ).toBeDisabled()
      expect(screen.getByText('Saisissez une contremarque')).toBeInTheDocument()
    })

    it('should display a message while the user is typing a token', () => {
      // given
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'ABCDE' } })

      // then
      expect(
        screen.getByRole('button', { name: 'Valider la contremarque' })
      ).toBeDisabled()
      expect(screen.getByText('Caractères restants : 1/6')).toBeInTheDocument()
    })

    it('should display a message when token is invalid', () => {
      // given
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'ù^`@' } })

      // then
      expect(
        screen.getByRole('button', { name: 'Valider la contremarque' })
      ).toBeDisabled()
      expect(
        screen.getByText('Caractères valides : de A à Z et de 0 à 9')
      ).toBeInTheDocument()
    })
  })

  it('should not validate the form when token is valid then invalid', async () => {
    // given
    jest.spyOn(props, 'getBooking').mockResolvedValue()
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')
    await waitFor(() =>
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })
    )

    // when
    fireEvent.change(tokenInput, { target: { value: 'MEFA' } })

    // then
    const submitButton = screen.getByRole('button', {
      name: 'Valider la contremarque',
    })
    expect(submitButton).toBeDisabled()
  })

  it('should not invalidate the form when token is valid then invalid', async () => {
    // given
    jest.spyOn(props, 'getBooking').mockResolvedValue(
      Promise.reject({
        errors: { booking: 'token is already validated' },
        status: 410,
      })
    )
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')
    await waitFor(() =>
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })
    )

    // when
    fireEvent.change(tokenInput, { target: { value: 'MEFA' } })

    // then
    const submitButton = screen.getByRole('button', {
      name: 'Valider la contremarque',
    })
    expect(submitButton).toBeDisabled()
  })

  describe('when the input field is filled with a valid token', () => {
    it('should display a message and booking informations', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockResolvedValue({
        datetime: '2020-10-23T20:00:00Z',
        offerName: 'Fake offer',
        userName: 'Fake user name',
        price: 40,
        ean13: 'isbn',
      })
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })

      // then
      expect(screen.getByText('Vérification...')).toBeInTheDocument()
      const submitButton = await screen.findByRole('button', {
        name: 'Valider la contremarque',
      })
      expect(submitButton).toBeEnabled()
      const responseFromApi = await screen.findByText(
        'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
      )
      expect(responseFromApi).toBeInTheDocument()
      const bookingUser = await queryByTextTrimHtml(
        screen,
        'Utilisateur : Fake user name'
      )
      expect(bookingUser).toBeInTheDocument()
      const bookingOffer = await queryByTextTrimHtml(
        screen,
        'Offre : Fake offer'
      )
      expect(bookingOffer).toBeInTheDocument()
      const bookingDate = await queryByTextTrimHtml(
        screen,
        'Date de l’offre : 23/10/2020 - 22h00'
      )
      expect(bookingDate).toBeInTheDocument()
      const bookingPrice = await queryByTextTrimHtml(screen, 'Prix : 40 €')
      expect(bookingPrice).toBeInTheDocument()
      const bookingIsbn = await queryByTextTrimHtml(screen, 'ISBN : isbn')
      expect(bookingIsbn).toBeInTheDocument()
    })

    it('should display isbn line with empty informations if offer is a book', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockResolvedValue({
        datetime: '2020-10-23T20:00:00Z',
        offerName: 'Fake offer',
        userName: 'Fake user name',
        price: 40,
        ean13: '',
      })
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })

      // then
      await screen.findByRole('button', { name: 'Valider la contremarque' })
      const bookingIsbn = await queryByTextTrimHtml(screen, 'ISBN :')
      expect(bookingIsbn).toBeInTheDocument()
    })

    it('should not display isbn line if offer is not a book', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockResolvedValue({
        datetime: '2020-10-23T20:00:00Z',
        offerName: 'Fake offer',
        userName: 'Fake user name',
        price: 40,
        ean13: null,
      })
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })

      // then
      await screen.findByRole('button', { name: 'Valider la contremarque' })
      const bookingIsbn = await queryByTextTrimHtml(screen, 'ISBN :')
      expect(bookingIsbn).not.toBeInTheDocument()
    })

    it('should display an error message when token validation fails', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockRejectedValue({
        errors: { booking: 'token validation is failed' },
        status: 410,
      })
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })

      // then
      const errorMessage = await screen.findByText('token validation is failed')
      expect(errorMessage).toBeInTheDocument()
    })

    it('should display a message and can invalidated the token when token is already validated', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockRejectedValue({
        errors: { booking: 'token is already validated' },
        status: 410,
      })
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      // when
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })

      // then
      const errorMessage = await screen.findByText('token is already validated')
      expect(errorMessage).toBeInTheDocument()
      const submitButton = await screen.findByRole('button', {
        name: 'Invalider la contremarque',
      })
      expect(submitButton).toBeEnabled()
    })
  })

  describe('when I can submit the form', () => {
    it('should display a message when booking is validated', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockResolvedValue()
      jest.spyOn(props, 'validateBooking').mockResolvedValue()
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')
      const submitButton = screen.getByRole('button', {
        name: 'Valider la contremarque',
      })

      expect(submitButton).toBeDisabled()
      await waitFor(() =>
        fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })
      )

      // when
      expect(submitButton).toBeEnabled()
      fireEvent.click(submitButton)

      // then
      expect(screen.getByText('Validation en cours...')).toBeInTheDocument()
      const responseFromApi = await screen.findByText('Contremarque validée !')
      expect(responseFromApi).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })

    it('should display a message when booking is invalidated', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockRejectedValue({
        errors: { booking: 'token is already validated' },
        status: 410,
      })
      jest.spyOn(props, 'invalidateBooking').mockResolvedValue()
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')

      const validateTokenButton = screen.getByRole('button', {
        name: 'Valider la contremarque',
      })
      expect(validateTokenButton).toBeDisabled()

      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })
      const invalidateTokenButton = await screen.findByRole('button', {
        name: 'Invalider la contremarque',
      })

      // when
      expect(invalidateTokenButton).toBeEnabled()
      fireEvent.click(invalidateTokenButton)

      const confirmInvalidateTokenButton = await screen.findByRole('button', {
        name: 'Continuer',
      })
      fireEvent.click(confirmInvalidateTokenButton)

      // then
      expect(screen.getByText('Invalidation en cours...')).toBeInTheDocument()
      const responseFromApi = await screen.findByText(
        'Contremarque invalidée !'
      )
      expect(responseFromApi).toBeInTheDocument()
      expect(validateTokenButton).toBeDisabled()
    })

    it('should display an error message when the booking validation has failed', async () => {
      // given
      jest.spyOn(props, 'getBooking').mockResolvedValue()
      jest.spyOn(props, 'validateBooking').mockRejectedValue({
        errors: { booking: 'error message' },
        status: 401,
      })
      renderDesk(props)
      const tokenInput = screen.getByLabelText('Contremarque')
      const submitButton = screen.getByRole('button', {
        name: 'Valider la contremarque',
      })
      await waitFor(() =>
        fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })
      )

      // when
      fireEvent.click(submitButton)

      // then
      const responseFromApi = await screen.findByText('error message')
      expect(responseFromApi).toBeInTheDocument()
    })

    it('should display an error message when the booking invalidation has failed', async () => {
      // given
      renderDesk(props)

      jest.spyOn(props, 'getBooking').mockRejectedValue({
        errors: { booking: 'token is already validated' },
        status: 410,
      })
      // when
      const tokenInput = screen.getByLabelText('Contremarque')
      fireEvent.change(tokenInput, { target: { value: 'MEFA01' } })
      // then
      await expect(
        screen.findByText('token is already validated')
      ).resolves.toBeInTheDocument()
      // when
      jest.spyOn(props, 'invalidateBooking').mockRejectedValue({
        errors: { booking: 'cannot invalidate booking' },
        status: 403,
      })
      const submitButton = await screen.findByRole('button', {
        name: 'Invalider la contremarque',
      })
      fireEvent.click(submitButton)

      const confirmInvalidateTokenButton = await screen.findByRole('button', {
        name: 'Continuer',
      })
      fireEvent.click(confirmInvalidateTokenButton)
      // then
      const responseFromApi = await screen.findByText(
        'cannot invalidate booking'
      )
      expect(responseFromApi).toBeInTheDocument()
    })
  })

  it('should display an informative message', () => {
    // When
    renderDesk(props)

    // Then
    const bannerMessage = queryByTextTrimHtml(
      screen,
      'N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque. Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique.',
      { selector: 'p' }
    )
    expect(bannerMessage).toBeInTheDocument()
    expect(
      screen.getByText('En savoir plus', { selector: 'a' }).getAttribute('href')
    ).toBe(
      'https://aide.passculture.app/hc/fr/articles/4416062183569--Acteurs-Culturels-Modalités-de-retrait-et-CGU'
    )
  })
})
