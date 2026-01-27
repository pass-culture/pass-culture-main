import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ActivationCodeFormDialog } from './ActivationCodeFormDialog'

vi.mock('./ActivationCodeFileChecker', () => ({
  checkAndParseUploadedFile: vi.fn(async () => ({
    errorMessage: '',
    activationCodes: ['CODE1', 'CODE2'],
  })),
  fileReader: {},
}))

const LABELS = {
  title: 'Ajouter des codes d’activation',
  fileInput: 'Importer un fichier .csv depuis l’ordinateur',
  validate: 'Valider',
  back: 'Retour',
  date: 'Date limite de validité',
}

describe('ActivationCodeFormDialog', () => {
  const today = new Date('2025-09-17T12:00:00Z')
  const minExpirationDate = new Date('2025-09-18T12:00:00Z')
  const ref = { current: document.createElement('button') }

  it('should not render dialog when closed', () => {
    renderWithProviders(
      <ActivationCodeFormDialog
        onCancel={vi.fn()}
        onSubmit={vi.fn()}
        today={today}
        minExpirationDate={minExpirationDate}
        isDialogOpen={false}
        activationCodeButtonRef={ref}
        departmentCode={'75'}
      />
    )

    expect(screen.queryByText(LABELS.title)).toBeFalsy()
  })

  it('should render initial upload form when open', () => {
    renderWithProviders(
      <ActivationCodeFormDialog
        onCancel={vi.fn()}
        onSubmit={vi.fn()}
        today={today}
        minExpirationDate={minExpirationDate}
        isDialogOpen
        activationCodeButtonRef={ref}
        departmentCode={'75'}
      />
    )

    expect(screen.getByText(LABELS.title)).toBeInTheDocument()
    expect(screen.getByLabelText(LABELS.fileInput)).toBeInTheDocument()
  })

  it('should go to confirmation step after valid file upload', async () => {
    const onSubmit = vi.fn()

    renderWithProviders(
      <ActivationCodeFormDialog
        onCancel={vi.fn()}
        onSubmit={onSubmit}
        today={today}
        minExpirationDate={minExpirationDate}
        isDialogOpen
        activationCodeButtonRef={ref}
        departmentCode={'75'}
      />
    )

    const fileInput = screen.getByLabelText(
      LABELS.fileInput
    ) as HTMLInputElement
    const file = new File(['CODE1\nCODE2'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(fileInput, file)

    expect(
      screen.getByText(/Vous êtes sur le point d’ajouter 2 codes d’activation./)
    ).toBeInTheDocument()
  })

  it('should submit activation codes with selected date', async () => {
    const onSubmit = vi.fn()

    renderWithProviders(
      <ActivationCodeFormDialog
        onCancel={vi.fn()}
        onSubmit={onSubmit}
        today={today}
        minExpirationDate={minExpirationDate}
        isDialogOpen
        activationCodeButtonRef={ref}
        departmentCode={'75'}
      />
    )

    const fileInput = screen.getByLabelText(
      LABELS.fileInput
    ) as HTMLInputElement
    const file = new File(['CODE1\nCODE2'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(fileInput, file)
    const dateInput = screen.getByLabelText(LABELS.date) as HTMLInputElement
    await userEvent.type(dateInput, '2025-10-02')
    await userEvent.click(screen.getByRole('button', { name: LABELS.validate }))

    expect(onSubmit).toHaveBeenCalledWith(['CODE1', 'CODE2'], '2025-10-02')
  })

  it('should allow cancelling (Retour) and closing dialog without submit', async () => {
    const onCancel = vi.fn()

    renderWithProviders(
      <ActivationCodeFormDialog
        onCancel={onCancel}
        onSubmit={vi.fn()}
        today={today}
        minExpirationDate={minExpirationDate}
        isDialogOpen
        activationCodeButtonRef={ref}
        departmentCode={'75'}
      />
    )

    const fileInput = screen.getByLabelText(
      LABELS.fileInput
    ) as HTMLInputElement
    const file = new File(['CODE1\nCODE2'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(fileInput, file)
    await userEvent.click(screen.getByRole('button', { name: LABELS.back }))

    expect(onCancel).toHaveBeenCalled()
  })
})
