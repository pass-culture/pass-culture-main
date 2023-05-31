import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { format } from 'date-fns'
import React from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import RequestFormDialog, { RequestFormDialogProps } from '../RequestFormDialog'

const renderRequestFormDialog = (props?: Partial<RequestFormDialogProps>) => {
  renderWithProviders(
    <RequestFormDialog
      closeModal={jest.fn()}
      venueName={'Venue 1'}
      offererName={'Offerer 1'}
      offerId={1}
      userEmail={'contact@example.com'}
      userRole={AdageFrontRoles.REDACTOR}
      {...props}
    />
  )
}

jest.mock('apiClient/api', () => ({
  apiAdage: {
    createCollectiveRequest: jest.fn(),
    logRequestFormPopinDismiss: jest.fn(),
  },
}))

describe('RequestFormDialog', () => {
  it('should display venueName and offererName', () => {
    renderRequestFormDialog()

    expect(screen.getByText('Venue 1 - Offerer 1')).toBeInTheDocument()
  })

  it('should display user email', () => {
    renderRequestFormDialog()

    expect(screen.getByLabelText('E-Mail')).toHaveValue('contact@example.com')
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
    const dateField = screen.getByLabelText('Date souhaitée', {
      exact: false,
    })

    await userEvent.type(descriptionField, 'Test description')
    await userEvent.click(dateField)
    const dates = screen.queryAllByText(new Date().getDate())
    await userEvent.click(dates[dates.length - 1])

    const submitButton = screen.getByRole('button', {
      name: 'Envoyer ma demande',
    })
    await userEvent.click(submitButton)
    expect(apiAdage.createCollectiveRequest).toHaveBeenCalledWith(1, {
      comment: 'Test description',
      phoneNumber: undefined,
      requestedDate: format(new Date(), 'yyyy-MM-dd'),
      totalTeachers: undefined,
      totalStudents: undefined,
    })
    expect(notifySuccess).toHaveBeenCalledWith(
      'Votre demande a bien été envoyée'
    )
    expect(mockCloseModal).toHaveBeenCalled()
  })
  it('should display error message when api reject call', async () => {
    jest.spyOn(apiAdage, 'createCollectiveRequest').mockRejectedValueOnce({})
    const notifyError = jest.fn()
    const mockCloseModal = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: jest.fn(),
      error: notifyError,
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

    expect(notifyError).toHaveBeenCalledWith(
      'Impossible de créer la demande.\nVeuillez contacter le support pass culture'
    )
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

  it('should not display form if user is readonly', () => {
    renderRequestFormDialog({ userRole: AdageFrontRoles.READONLY })

    expect(
      screen.queryByText(
        'Si vous le souhaitez, vous pouvez contacter ce partenaire culturel en renseignant les informations ci-dessous.'
      )
    ).not.toBeInTheDocument()
  })
  it('should log event when user close modal', async () => {
    const mockCloseModal = jest.fn()
    renderRequestFormDialog({ closeModal: mockCloseModal })

    const descriptionField = screen.getByLabelText(
      'Que souhaitez vous organiser ?'
    )
    await userEvent.type(descriptionField, 'Test description')

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Annuler',
      })
    )

    expect(apiAdage.logRequestFormPopinDismiss).toHaveBeenCalledWith({
      collectiveOfferTemplateId: 1,
      comment: 'Test description',
      phoneNumber: undefined,
      requestedDate: undefined,
      totalStudents: undefined,
      totalTeachers: undefined,
    })
  })
})
