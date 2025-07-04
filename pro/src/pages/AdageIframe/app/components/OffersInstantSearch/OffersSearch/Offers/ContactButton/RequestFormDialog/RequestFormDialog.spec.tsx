import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { format } from 'date-fns'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import * as useNotification from 'commons/hooks/useNotification'
import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { RequestFormDialog, RequestFormDialogProps } from './RequestFormDialog'

const renderRequestFormDialog = (props?: Partial<RequestFormDialogProps>) => {
  renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <RequestFormDialog
          onConfirmDialog={vi.fn()}
          offerId={1}
          userEmail={'contact@example.com'}
          userRole={AdageFrontRoles.REDACTOR}
          contactEmail=""
          contactForm="form"
          contactPhone=""
          contactUrl=""
          isPreview={false}
          {...props}
        />{' '}
      </Dialog.Content>
    </Dialog.Root>
  )
}

vi.mock('apiClient/api', () => ({
  apiAdage: {
    createCollectiveRequest: vi.fn(),
    logRequestFormPopinDismiss: vi.fn(),
    logContactUrlClick: vi.fn(),
  },
}))

describe('RequestFormDialog', () => {
  it('should display passCulture default form', () => {
    renderRequestFormDialog({
      contactEmail: '',
      contactPhone: '',
      contactForm: 'form',
      contactUrl: '',
    })

    expect(screen.getByLabelText('Email *')).toHaveValue('contact@example.com')
  })

  it('should only display mail ', () => {
    renderRequestFormDialog({
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
    renderRequestFormDialog({
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
    renderRequestFormDialog({
      contactEmail: '',
      contactPhone: '',
      contactForm: '',
      contactUrl: 'https://example.com',
    })

    const buttonLink = screen.getByText('Aller sur le site')

    expect(buttonLink).toHaveAttribute('href', 'https://example.com')
  })

  it('should display mail and phone', () => {
    renderRequestFormDialog({
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
    renderRequestFormDialog({
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
    renderRequestFormDialog({
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
      close: vi.fn(),
    }))

    renderRequestFormDialog({ onConfirmDialog: mockCloseModal })

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
      totalTeachers: 0,
      totalStudents: 0,
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
      close: vi.fn(),
    }))

    renderRequestFormDialog({ onConfirmDialog: mockCloseModal })

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
      screen.getByText('Veuillez renseigner un numéro de téléphone valide')
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
    renderRequestFormDialog({ onConfirmDialog: mockCloseModal })

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
      phoneNumber: '',
      requestedDate: undefined,
      totalStudents: 0,
      totalTeachers: 0,
    })
  })

  it('should log event when user click on custom link form', async () => {
    renderRequestFormDialog({
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
