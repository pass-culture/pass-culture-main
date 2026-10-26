import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { FileUploadItem } from './FileUploadItem'

const file = new File(['a'.repeat(3_000_000)], 'Nom du fichier.pdf', {
  type: 'application/pdf',
})

function renderFileUploadItem(
  props?: Partial<React.ComponentProps<typeof FileUploadItem>>
) {
  return render(
    <ul>
      <FileUploadItem file={file} onDelete={vi.fn()} {...props} />
    </ul>
  )
}

describe('FileUploadItem', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderFileUploadItem({ status: 'error' })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the name and the size of the file', () => {
    renderFileUploadItem()

    expect(screen.getByText('Nom du fichier.pdf')).toBeInTheDocument()
    expect(screen.getByText('3 Mo')).toBeInTheDocument()
    expect(screen.getByRole('status')).toBeEmptyDOMElement()
  })

  it.each([
    { status: 'success' as const, label: 'Fichier ajouté' },
    {
      status: 'error' as const,
      label:
        'Une erreur est survenue. Veuillez télécharger à nouveau le fichier.',
    },
  ])('should announce the $status status', ({ status, label }) => {
    renderFileUploadItem({ status })

    expect(screen.getByRole('status')).toHaveTextContent(label)
  })

  it('should delete the file', async () => {
    const onDelete = vi.fn()
    renderFileUploadItem({ onDelete })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer Nom du fichier.pdf' })
    )

    expect(onDelete).toHaveBeenCalledOnce()
  })

  it('should disable the delete button', () => {
    renderFileUploadItem({ disabled: true })

    expect(
      screen.getByRole('button', { name: 'Supprimer Nom du fichier.pdf' })
    ).toBeDisabled()
  })
})
