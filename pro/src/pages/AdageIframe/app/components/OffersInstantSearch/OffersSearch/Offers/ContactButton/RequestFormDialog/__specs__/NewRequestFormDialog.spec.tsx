import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { format } from 'date-fns'
import React from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  NewRequestFormDialog,
  NewRequestFormDialogProps,
} from '../NewRequestFormDialog'

const renderNewRequestFormDialog = (
  props?: Partial<NewRequestFormDialogProps>
) => {
  renderWithProviders(
    <NewRequestFormDialog
      closeModal={vi.fn()}
      offerId={1}
      userEmail={'contact@example.com'}
      userRole={AdageFrontRoles.REDACTOR}
      contactEmail=""
      contactForm="form"
      contactPhone=""
      contactUrl=""
      isPreview={false}
      {...props}
    />
  )
}

vi.mock('apiClient/api', () => ({
  apiAdage: {
    createCollectiveRequest: vi.fn(),
    logRequestFormPopinDismiss: vi.fn(),
    logContactUrlClick: vi.fn(),
  },
}))

describe('NewRequestFormDialog', () => {
  it('should display passCulture default form', () => {
    renderNewRequestFormDialog({
      contactEmail: '',
      contactPhone: '',
      contactForm: 'form',
      contactUrl: '',
    })

    expect(screen.getByLabelText('Email *')).toHaveValue('contact@example.com')
  })

  it('should only display mail ', () => {
    renderNewRequestFormDialog({
      contactEmail: 'test@example.com',
      contactPhone: '',
      contactForm: '',
      contactUrl: '',
    })

    expect(
      screen.getByText('Il vous propose de le faire par mail :')
    ).toBeInTheDocument()
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
  })

  it('should only display phone number', () => {
    renderNewRequestFormDialog({
      contactEmail: '',
      contactPhone: '0600000000',
      contactForm: '',
      contactUrl: '',
    })

    expect(
      screen.getByText('Il vous propose de le faire par téléphone :')
    ).toBeInTheDocument()
    expect(screen.getByText('0600000000')).toBeInTheDocument()
  })

  it('should only display buttonlink of custom form', () => {
    renderNewRequestFormDialog({
      contactEmail: '',
      contactPhone: '',
      contactForm: '',
      contactUrl: 'https://example.com',
    })

    const buttonLink = screen.getByText('Aller sur le site')

    expect(buttonLink).toHaveAttribute('href', 'https://example.com')
  })

  it('should display mail and phone', () => {
    renderNewRequestFormDialog({
      contactEmail: 'test@example.com',
      contactPhone: '0600000000',
      contactForm: '',
      contactUrl: '',
    })

    expect(
      screen.getByText('Il vous propose de le faire :')
    ).toBeInTheDocument()

    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByText('0600000000')).toBeInTheDocument()
  })

  it('should display mail and phone and passCulture default form', () => {
    renderNewRequestFormDialog({
      contactEmail: 'test@example.com',
      contactPhone: '0600000000',
      contactForm: 'form',
      contactUrl: '',
    })

    expect(
      screen.getByText('Il vous propose de le faire :')
    ).toBeInTheDocument()

    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByText('0600000000')).toBeInTheDocument()
    expect(screen.getByLabelText('Email *')).toHaveValue('contact@example.com')
  })

  it('should display mail and phone and custom form', () => {
    renderNewRequestFormDialog({
      contactEmail: 'test@example.com',
      contactPhone: '0600000000',
      contactForm: '',
      contactUrl: 'https://example.com',
    })

    expect(
      screen.getByText('Il vous propose de le faire :')
    ).toBeInTheDocument()

    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByText('0600000000')).toBeInTheDocument()

    const buttonLink = screen.getByText('Aller sur le site')

    expect(buttonLink).toHaveAttribute('href', 'https://example.com')
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

    renderNewRequestFormDialog({ closeModal: mockCloseModal })

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

    renderNewRequestFormDialog({ closeModal: mockCloseModal })

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
    renderNewRequestFormDialog()

    const submitButton = screen.getByRole('button', {
      name: 'Envoyer ma demande',
    })
    await userEvent.click(submitButton)

    expect(
      screen.getByText('Veuillez préciser votre demande')
    ).toBeInTheDocument()
  })

  it('should display error message when phone number is not valid', async () => {
    renderNewRequestFormDialog()

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
    renderNewRequestFormDialog({ userRole: AdageFrontRoles.READONLY })

    expect(
      screen.queryByText(
        'Si vous le souhaitez, vous pouvez contacter ce partenaire culturel en renseignant les informations ci-dessous.'
      )
    ).not.toBeInTheDocument()
  })

  it('should log event when user close modal', async () => {
    const mockCloseModal = vi.fn()
    renderNewRequestFormDialog({ closeModal: mockCloseModal })

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

  it('should log event when user click on custom link form', async () => {
    renderNewRequestFormDialog({
      contactEmail: '',
      contactPhone: '',
      contactForm: '',
      contactUrl: 'https://example.com',
    })

    const buttonLink = screen.getByText('Aller sur le site')

    await userEvent.click(buttonLink)

    expect(apiAdage.logContactUrlClick).toHaveBeenCalledWith({
      iframeFrom: '/',
      offerId: 1,
    })
  })
})
