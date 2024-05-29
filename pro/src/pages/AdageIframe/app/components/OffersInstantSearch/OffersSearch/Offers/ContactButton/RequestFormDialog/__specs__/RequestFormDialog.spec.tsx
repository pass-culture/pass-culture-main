import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { format } from 'date-fns'
import React from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import { RequestFormDialog, RequestFormDialogProps } from '../RequestFormDialog'

const renderRequestFormDialog = (props?: Partial<RequestFormDialogProps>) => {
  renderWithProviders(
    <RequestFormDialog
      closeModal={vi.fn()}
      offerId={1}
      userEmail={'contact@example.com'}
      userRole={AdageFrontRoles.REDACTOR}
      {...props}
      isPreview={false}
    />
  )
}

vi.mock('apiClient/api', () => ({
  apiAdage: {
    createCollectiveRequest: vi.fn(),
    logRequestFormPopinDismiss: vi.fn(),
  },
}))

describe('RequestFormDialog', () => {
  it('should display user email', () => {
    renderRequestFormDialog()

    expect(screen.getByLabelText('Email *')).toHaveValue('contact@example.com')
  })

  it('should submit valid form and close modal on submit', async () => {
    const notifySuccess = vi.fn()
    const mockCloseModal = vi.fn()
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      success: notifySuccess,
      error: vi.fn(),
      information: vi.fn(),
      pending: vi.fn(),
      close: vi.fn(),
    }))

    renderRequestFormDialog({ closeModal: mockCloseModal })

    const today = format(new Date(), FORMAT_ISO_DATE_ONLY)
    await userEvent.type(
      screen.getByLabelText('Que souhaitez vous organiser ? *'),
      'Test description'
    )
    await userEvent.type(
      screen.getByLabelText('Date souhaitée', { exact: false }),
      today
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Envoyer ma demande' })
    )

    expect(apiAdage.createCollectiveRequest).toHaveBeenCalledWith(1, {
      comment: 'Test description',
      phoneNumber: undefined,
      requestedDate: today,
      totalTeachers: undefined,
      totalStudents: undefined,
    })
    expect(notifySuccess).toHaveBeenCalledWith(
      'Votre demande a bien été envoyée'
    )
    expect(mockCloseModal).toHaveBeenCalled()
  })
  it('should display error message when api reject call', async () => {
    vi.spyOn(apiAdage, 'createCollectiveRequest').mockRejectedValueOnce({})
    const notifyError = vi.fn()
    const mockCloseModal = vi.fn()
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      success: vi.fn(),
      error: notifyError,
      information: vi.fn(),
      pending: vi.fn(),
      close: vi.fn(),
    }))

    renderRequestFormDialog({ closeModal: mockCloseModal })

    const descriptionField = screen.getByLabelText(
      'Que souhaitez vous organiser ? *'
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
      screen.getByText(
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
      )
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
    const mockCloseModal = vi.fn()
    renderRequestFormDialog({ closeModal: mockCloseModal })

    const descriptionField = screen.getByLabelText(
      'Que souhaitez vous organiser ? *'
    )
    await userEvent.type(descriptionField, 'Test description')

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Annuler',
      })
    )

    expect(apiAdage.logRequestFormPopinDismiss).toHaveBeenCalledWith({
      iframeFrom: '/',
      collectiveOfferTemplateId: 1,
      comment: 'Test description',
      phoneNumber: undefined,
      requestedDate: undefined,
      totalStudents: undefined,
      totalTeachers: undefined,
    })
  })
})
