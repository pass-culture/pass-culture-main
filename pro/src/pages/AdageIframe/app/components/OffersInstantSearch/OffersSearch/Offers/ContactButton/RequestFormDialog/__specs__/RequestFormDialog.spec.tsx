import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import RequestFormDialog, { RequestFormDialogProps } from '../RequestFormDialog'

const renderRequestFormDialog = (props?: Partial<RequestFormDialogProps>) => {
  renderWithProviders(
    <RequestFormDialog
      closeModal={jest.fn()}
      venueName={'Venue 1'}
      offererName={'Offerer 1'}
      {...props}
    />
  )
}

describe('RequestFormDialog', () => {
  it('should display venueName and offererName', () => {
    renderRequestFormDialog()

    expect(screen.getByText('Venue 1 - Offerer 1')).toBeInTheDocument()
  })

  it('should submit valid form and close modal on submit', async () => {
    const notifySuccess = jest.fn()
    const mockCloseModal = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: notifySuccess,
      error: jest.fn(),
      information: jest.fn(),
      pending: jest.fn(),
      close: jest.fn(),
    }))

    renderRequestFormDialog({ closeModal: mockCloseModal })

    const descriptionField = screen.getByLabelText(
      'Que souhaitez vous organiser ?'
    )
    await userEvent.type(descriptionField, 'Test description')

    const submitButton = screen.getByRole('button', {
      name: 'Envoyer ma demande',
    })
    await userEvent.click(submitButton)
    expect(notifySuccess).toHaveBeenCalledWith(
      'Votre demande a bien été envoyée'
    )
    expect(mockCloseModal).toHaveBeenCalled()
  })

  it('should display error message when description is empty', async () => {
    renderRequestFormDialog()

    const submitButton = screen.getByRole('button', {
      name: 'Envoyer ma demande',
    })
    await userEvent.click(submitButton)

    expect(
      screen.getByText('Veuillez préciser votre demande')
    ).toBeInTheDocument()
  })

  it('should display error message when phone number is not valid', async () => {
    renderRequestFormDialog()

    const phoneField = screen.getByLabelText('Téléphone', { exact: false })
    await userEvent.type(phoneField, '123')

    const submitButton = screen.getByRole('button', {
      name: 'Envoyer ma demande',
    })
    await userEvent.click(submitButton)

    expect(
      screen.getByText('Veuillez entrer un numéro de téléphone valide')
    ).toBeInTheDocument()
  })
})
