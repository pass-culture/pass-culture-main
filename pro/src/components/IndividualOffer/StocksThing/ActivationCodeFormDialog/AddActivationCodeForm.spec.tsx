import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AddActivationCodeForm } from './AddActivationCodeForm'

const LABELS = {
  fileInput: 'Importer un fichier .csv depuis l’ordinateur',
  template: 'Gabarit CSV',
}

describe('AddActivationCodeForm', () => {
  it('should render upload info description and file input enabled when no error', () => {
    const submitFile = vi.fn()

    renderWithProviders(
      <AddActivationCodeForm
        submitFile={submitFile}
        isFileInputDisabled={false}
        errorMessage=""
      />
    )

    expect(screen.getByLabelText(LABELS.fileInput)).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Gabarit CSV/ })
    ).toBeInTheDocument()
    expect(screen.getByLabelText(LABELS.fileInput)).not.toBeDisabled()
  })

  it('should show error block and mark input invalid when errorMessage provided', () => {
    const submitFile = vi.fn()

    renderWithProviders(
      <AddActivationCodeForm
        submitFile={submitFile}
        isFileInputDisabled={false}
        errorMessage="Wrong format"
      />
    )

    expect(
      screen.getByText(
        'Une erreur s’est produite lors de l’import de votre fichier.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Wrong format')).toBeInTheDocument()
  })

  it('should disable file input when isFileInputDisabled', () => {
    const submitFile = vi.fn()

    renderWithProviders(
      <AddActivationCodeForm
        submitFile={submitFile}
        isFileInputDisabled={true}
        errorMessage=""
      />
    )

    expect(screen.getByLabelText(LABELS.fileInput)).toBeDisabled()
  })

  it('should call submitFile on file selection', async () => {
    const submitFile = vi.fn()

    renderWithProviders(
      <AddActivationCodeForm
        submitFile={submitFile}
        isFileInputDisabled={false}
        errorMessage=""
      />
    )

    const input = screen.getByLabelText(LABELS.fileInput) as HTMLInputElement
    const file = new File(['code'], 'codes.csv', { type: 'text/csv' })
    await userEvent.upload(input, file)

    expect(submitFile).toHaveBeenCalledTimes(1)
  })
})
