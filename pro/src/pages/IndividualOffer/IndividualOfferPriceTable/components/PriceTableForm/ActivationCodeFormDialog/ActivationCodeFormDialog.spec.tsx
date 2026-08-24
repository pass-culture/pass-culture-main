import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  ActivationCodeFileErrorCode,
  checkAndParseUploadedFile,
} from './ActivationCodeFileChecker'
import { ActivationCodeFormDialog } from './ActivationCodeFormDialog'

vi.mock('./ActivationCodeFileChecker', async (importOriginal) => {
  const actual =
    await importOriginal<typeof import('./ActivationCodeFileChecker')>()

  return {
    ...actual,
    checkAndParseUploadedFile: vi.fn(async () => ({
      activationCodes: ['CODE1', 'CODE2'],
    })),
    fileReader: {},
  }
})

const LABELS = {
  title: 'Ajouter des codes d’activation 1/2',
  fileInput: 'Importer un fichier .csv depuis l’ordinateur',
  validate: 'Ajouter les codes de validation',
  back: 'Retour à l’étape d’import',
  date: 'Date de fin de validité *',
}

describe('ActivationCodeFormDialog', () => {
  const mockedCheckAndParseUploadedFile = vi.mocked(checkAndParseUploadedFile)
  const today = new Date('2025-09-17T12:00:00Z')
  const minExpirationDate = new Date('2025-09-18T12:00:00Z')
  const ref = { current: document.createElement('button') }

  beforeEach(() => {
    mockedCheckAndParseUploadedFile.mockResolvedValue({
      activationCodes: ['CODE1', 'CODE2'],
    })
  })

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

  it('should disable validation button until reservation date is set', async () => {
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

    const fileInput = screen.getByLabelText(
      LABELS.fileInput
    ) as HTMLInputElement
    const file = new File(['CODE1\nCODE2'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(fileInput, file)

    expect(screen.getByRole('button', { name: LABELS.validate })).toBeDisabled()
  })

  it('should disable validation button again when reservation date is cleared', async () => {
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

    const fileInput = screen.getByLabelText(
      LABELS.fileInput
    ) as HTMLInputElement
    const file = new File(['CODE1\nCODE2'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(fileInput, file)

    const dateInput = screen.getByLabelText(LABELS.date) as HTMLInputElement
    await userEvent.type(dateInput, '2025-10-02')
    await userEvent.clear(dateInput)

    expect(screen.getByRole('button', { name: LABELS.validate })).toBeDisabled()
  })

  it('should go back to upload step when clicking Retour', async () => {
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
    await userEvent.click(
      screen.getByRole('button', {
        name: LABELS.back,
      })
    )

    expect(onCancel).not.toHaveBeenCalled()
    expect(screen.getByLabelText(LABELS.fileInput)).toBeInTheDocument()
  })

  it('should stay on step 1 and show invalid format banner when file format is invalid', async () => {
    mockedCheckAndParseUploadedFile.mockResolvedValueOnce({
      errorCode: ActivationCodeFileErrorCode.INVALID_FORMAT,
      errorMessage:
        'Le fichier ne respecte pas le format attendu. Merci de vous rapporter au gabarit CSV disponible au téléchargement.',
      activationCodes: undefined,
    })

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

    const fileInput = screen.getByLabelText(
      LABELS.fileInput
    ) as HTMLInputElement
    const file = new File(['bad;format'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(fileInput, file)

    expect(screen.getByText(LABELS.title)).toBeInTheDocument()
    expect(screen.getByText('Format invalide')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Le fichier ne respecte pas le format attendu. Merci de vous rapporter au gabarit CSV disponible au téléchargement.'
      )
    ).toBeInTheDocument()
  })

  it('should stay on step 1 and show too-large-file banner when file is too heavy', async () => {
    mockedCheckAndParseUploadedFile.mockResolvedValueOnce({
      errorCode: ActivationCodeFileErrorCode.FILE_TOO_LARGE,
      errorMessage:
        'Le fichier ne respecte pas le poids attendu. La taille maximale du fichier ne doit pas dépasser 1 Mo.',
      activationCodes: undefined,
    })

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

    const fileInput = screen.getByLabelText(
      LABELS.fileInput
    ) as HTMLInputElement
    const file = new File(['too-heavy'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(fileInput, file)

    expect(screen.getByText(LABELS.title)).toBeInTheDocument()
    expect(screen.getByText('Fichier trop lourd')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Le fichier ne respecte pas le poids attendu. La taille maximale du fichier ne doit pas dépasser 1 Mo.'
      )
    ).toBeInTheDocument()
  })
})
