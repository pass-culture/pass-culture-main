import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from 'utils/stubStore'

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

  it('should display title and a description', () => {
    // when
    renderDesk(props)

    // then
    const title = screen.getByText('Guichet', { selector: 'h1' })
    const description = screen.getByText(
      'Enregistrez les contremarques de réservations présentés par les porteurs du pass.'
    )
    expect(title).toBeInTheDocument()
    expect(description).toBeInTheDocument()
  })

  it('should display a text input', () => {
    // when
    renderDesk(props)

    // then
    const input = screen.getByPlaceholderText('ex : AZE123')
    expect(input).toHaveAttribute('maxLength', '6')
    expect(input).toHaveAttribute('type', 'text')
  })

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

  it('should display a message when is typing a token', () => {
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

  it('should display a message when token is checked', async () => {
    // given
    jest.spyOn(props, 'getBooking').mockImplementation(() => Promise.resolve())
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')

    // when
    fireEvent.change(tokenInput, { target: { value: 'ABCDEF' } })

    // then
    expect(screen.getByText('Vérification...')).toBeInTheDocument()
    const submitButton = await screen.findByRole('button', { name: 'Valider la contremarque' })
    expect(submitButton).toBeEnabled()
  })

  it('should display a message when token is valid', async () => {
    // given
    jest.spyOn(props, 'getBooking').mockImplementation(() =>
      Promise.resolve({
        datetime: null,
        offerName: 'Fake offer',
        userName: 'Fake user name',
      })
    )
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')

    // when
    fireEvent.change(tokenInput, { target: { value: '100001' } })

    // then
    const responseFromApi = await screen.findByText(
      'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
    )
    expect(responseFromApi).toBeInTheDocument()
    const label1 = await screen.findByText('Utilisateur :')
    expect(label1).toBeInTheDocument()
    const value1 = await screen.findByText('Fake user name')
    expect(value1).toBeInTheDocument()
    const label2 = await screen.findByText('Offre :')
    expect(label2).toBeInTheDocument()
    const value2 = await screen.findByText('Fake offer')
    expect(value2).toBeInTheDocument()
    const label3 = await screen.findByText('Date de l’offre :')
    expect(label3).toBeInTheDocument()
    const value3 = await screen.findByText('Permanent')
    expect(value3).toBeInTheDocument()
  })

  it('should display an error message when token is failed', async () => {
    // given
    jest
      .spyOn(props, 'getBooking')
      .mockImplementation(() =>
        Promise.reject({ json: jest.fn(() => Promise.resolve({ booking: 'error message' })) })
      )
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')

    // when
    fireEvent.change(tokenInput, { target: { value: '100001' } })

    // then
    const errorMessage = await screen.findByText('error message')
    expect(errorMessage).toBeInTheDocument()
  })

  it('should display a message when booking is registering', async () => {
    // given
    jest.spyOn(props, 'getBooking').mockImplementation(() =>
      Promise.resolve({
        datetime: null,
        offerName: 'Fake offer',
        userName: 'Fake user name',
      })
    )
    jest.spyOn(props, 'validateBooking').mockImplementation(() => Promise.resolve())
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')
    const submitButton = screen.getByRole('button', { name: 'Valider la contremarque' })
    await waitFor(() => fireEvent.change(tokenInput, { target: { value: '100001' } }))

    // when
    fireEvent.click(submitButton)

    // then
    expect(screen.getByText('Enregistrement en cours...')).toBeInTheDocument()
  })

  it('should display a message when booking is registered', async () => {
    // given
    jest.spyOn(props, 'getBooking').mockImplementation(() =>
      Promise.resolve({
        datetime: null,
        offerName: 'Fake offer',
        userName: 'Fake user name',
      })
    )
    jest.spyOn(props, 'validateBooking').mockImplementation(() => Promise.resolve())
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')
    const submitButton = screen.getByRole('button', { name: 'Valider la contremarque' })
    await waitFor(() => fireEvent.change(tokenInput, { target: { value: '100001' } }))

    // when
    fireEvent.click(submitButton)

    // then
    const responseFromApi = await screen.findByText('Enregistrement réussi !')
    expect(responseFromApi).toBeInTheDocument()
  })

  it('should display an error message when the booking is registering failed', async () => {
    // given
    jest.spyOn(props, 'getBooking').mockImplementation(() =>
      Promise.resolve({
        datetime: null,
        offerName: 'Fake offer',
        userName: 'Fake user name',
      })
    )
    jest
      .spyOn(props, 'validateBooking')
      .mockImplementation(() =>
        Promise.reject({ json: jest.fn(() => Promise.resolve({ booking: 'error message' })) })
      )
    renderDesk(props)
    const tokenInput = screen.getByLabelText('Contremarque')
    const submitButton = screen.getByRole('button', { name: 'Valider la contremarque' })
    await waitFor(() => fireEvent.change(tokenInput, { target: { value: '100001' } }))

    // when
    fireEvent.click(submitButton)

    // then
    const responseFromApi = await screen.findByText('error message')
    expect(responseFromApi).toBeInTheDocument()
  })
})
