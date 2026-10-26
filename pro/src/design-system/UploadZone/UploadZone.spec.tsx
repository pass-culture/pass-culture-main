import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { UploadZone, type UploadZoneProps } from './UploadZone'

const defaultProps: UploadZoneProps = {
  label: 'Justificatifs',
  accept: { 'application/pdf': ['.pdf'] },
  maxSize: 5_000_000,
}

function renderUploadZone(props?: Partial<UploadZoneProps>) {
  return render(
    <UploadZone {...defaultProps} {...(props as UploadZoneProps)} />
  )
}

function createFile(name = 'document.pdf', type = 'application/pdf') {
  return new File(['content'], name, { type })
}

function getDataTransfer(files: File[]) {
  return {
    dataTransfer: {
      files,
      items: files.map((file) => ({
        kind: 'file',
        type: file.type,
        getAsFile: () => file,
      })),
      types: ['Files'],
    },
  }
}

describe('UploadZone', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderUploadZone({
      description: 'Description du champ',
      maxFiles: 3,
      filesCount: 0,
      error: 'Veuillez ajouter un fichier',
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should describe the file input with its description, conditions and files counter', () => {
    renderUploadZone({
      description: 'Description du champ',
      maxFiles: 3,
      filesCount: 0,
    })

    const input = screen.getByLabelText('Justificatifs')
    expect(input).toHaveAttribute('type', 'file')
    expect(input).toHaveAttribute('accept', 'application/pdf,.pdf')
    expect(input).toHaveAttribute('multiple')
    expect(input).toHaveAccessibleDescription(
      /^Description du champ Formats acceptés : PDF\. Poids maximum : 5 Mo\. 0\/3 fichiers maximum$/
    )
  })

  it('should be named by its instruction when there is no label', () => {
    renderUploadZone({ label: undefined })

    expect(
      screen.getByLabelText('Téléchargez ou déposez le fichier ici')
    ).toBeInTheDocument()
  })

  it('should only accept a single file when maxFiles is 1', () => {
    renderUploadZone({ maxFiles: 1 })

    expect(screen.getByLabelText('Justificatifs')).not.toHaveAttribute(
      'multiple'
    )
  })

  it('should not display the files counter when used alone', () => {
    renderUploadZone({ maxFiles: 1 })

    expect(screen.queryByText(/fichiers? maximum/)).not.toBeInTheDocument()
    expect(screen.getByLabelText('Justificatifs')).toHaveAccessibleDescription(
      'Formats acceptés : PDF. Poids maximum : 5 Mo.'
    )
  })

  it('should show the required indicators', () => {
    const { rerender } = renderUploadZone({ required: true })

    expect(screen.getByText('*')).toBeInTheDocument()
    expect(screen.getByLabelText(/Justificatifs/)).toHaveAttribute(
      'aria-required',
      'true'
    )

    rerender(
      <UploadZone {...defaultProps} required requiredIndicator="explicit" />
    )

    expect(screen.getByText('Obligatoire')).toBeInTheDocument()
  })

  it('should call onFilesAdded with the selected files', async () => {
    const onFilesAdded = vi.fn()
    renderUploadZone({ onFilesAdded })
    const files = [createFile('a.pdf'), createFile('b.pdf')]

    await userEvent.upload(screen.getByLabelText('Justificatifs'), files)

    expect(onFilesAdded).toHaveBeenCalledWith(files)
  })

  it('should call onFilesAdded with the dropped files', async () => {
    const onFilesAdded = vi.fn()
    renderUploadZone({ onFilesAdded })
    const file = createFile()

    fireEvent.drop(
      screen.getByLabelText('Justificatifs'),
      getDataTransfer([file])
    )

    await waitFor(() => expect(onFilesAdded).toHaveBeenCalledWith([file]))
    expect(screen.getByRole('alert')).toBeEmptyDOMElement()
  })

  it('should change its instruction while a file is dragged over', async () => {
    renderUploadZone()

    fireEvent.dragEnter(
      screen.getByLabelText('Justificatifs'),
      getDataTransfer([createFile()])
    )

    expect(
      await screen.findByText('Déposez votre fichier ici')
    ).toBeInTheDocument()
  })

  it.each([
    {
      case: 'a file with a wrong format',
      file: createFile('image.png', 'image/png'),
      message: 'Le format du fichier n’est pas accepté.',
    },
    {
      case: 'a too heavy file',
      file: Object.defineProperty(createFile(), 'size', {
        value: 5_000_001,
      }),
      message: 'Le fichier est trop lourd.',
    },
    {
      case: 'an empty file',
      file: new File([], 'empty.pdf', { type: 'application/pdf' }),
      message: 'Le fichier est vide ou corrompu.',
    },
  ])('should reject $case', async ({ file, message }) => {
    const onFilesAdded = vi.fn()
    renderUploadZone({ onFilesAdded })
    const input = screen.getByLabelText('Justificatifs')

    fireEvent.drop(input, getDataTransfer([file]))

    expect(await screen.findByText(message)).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent(message)
    expect(input).toHaveAccessibleDescription(expect.stringContaining(message))
    expect(input).toBeInvalid()
    expect(input).toHaveFocus()
    expect(onFilesAdded).not.toHaveBeenCalled()
  })

  it('should reject an unreadable file', async () => {
    const file = createFile()
    vi.spyOn(file, 'slice').mockReturnValue(
      Object.assign(new Blob(), {
        arrayBuffer: () => Promise.reject(new Error('NotReadableError')),
      })
    )
    renderUploadZone()

    fireEvent.drop(
      screen.getByLabelText('Justificatifs'),
      getDataTransfer([file])
    )

    expect(
      await screen.findByText('Le fichier est vide ou corrompu.')
    ).toBeInTheDocument()
  })

  it('should display several errors at once', async () => {
    renderUploadZone()

    fireEvent.drop(
      screen.getByLabelText('Justificatifs'),
      getDataTransfer([
        createFile('image.png', 'image/png'),
        Object.defineProperty(createFile(), 'size', { value: 5_000_001 }),
      ])
    )

    expect(
      await screen.findByText('Le format du fichier n’est pas accepté.')
    ).toBeInTheDocument()
    expect(screen.getByText('Le fichier est trop lourd.')).toBeInTheDocument()
  })

  it('should only add the files fitting in the remaining slots', async () => {
    const onFilesAdded = vi.fn()
    renderUploadZone({ maxFiles: 3, filesCount: 2, onFilesAdded })
    const files = [createFile('a.pdf'), createFile('b.pdf')]

    fireEvent.drop(
      screen.getByLabelText('Justificatifs'),
      getDataTransfer(files)
    )

    expect(
      await screen.findByText('Vous ne pouvez pas ajouter plus de 3 fichiers.')
    ).toBeInTheDocument()
    expect(onFilesAdded).toHaveBeenCalledWith([files[0]])
  })

  it('should only add the first dropped file when maxFiles is 1', async () => {
    const onFilesAdded = vi.fn()
    renderUploadZone({ maxFiles: 1, onFilesAdded })
    const files = [createFile('a.pdf'), createFile('b.pdf')]

    fireEvent.drop(
      screen.getByLabelText('Justificatifs'),
      getDataTransfer(files)
    )

    expect(
      await screen.findByText('Vous ne pouvez ajouter qu’un seul fichier.')
    ).toBeInTheDocument()
    expect(onFilesAdded).toHaveBeenCalledWith([files[0]])
  })

  it('should display the error given by the form', () => {
    renderUploadZone({ error: 'Veuillez ajouter un fichier' })

    expect(screen.getByRole('alert')).toHaveTextContent(
      'Veuillez ajouter un fichier'
    )
    expect(screen.getByLabelText('Justificatifs')).toBeInvalid()
  })

  it('should disable the file input', () => {
    renderUploadZone({ disabled: true })

    expect(screen.getByLabelText('Justificatifs')).toBeDisabled()
  })

  describe('when the maximum number of files is reached', () => {
    it('should keep the file input focusable to read the files counter', async () => {
      renderUploadZone({ maxFiles: 3, filesCount: 3 })
      const input = screen.getByLabelText('Justificatifs')

      await userEvent.tab()

      expect(input).toHaveFocus()
      expect(input).toBeEnabled()
      expect(input).toHaveAttribute('aria-disabled', 'true')
      expect(input).toHaveAccessibleDescription(
        expect.stringContaining('3/3 fichiers maximum')
      )
    })

    it('should not open the file picker', () => {
      renderUploadZone({ maxFiles: 3, filesCount: 3 })

      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
      })
      screen.getByLabelText('Justificatifs').dispatchEvent(clickEvent)

      expect(clickEvent.defaultPrevented).toBe(true)
    })

    it('should ignore dropped files', async () => {
      const onFilesAdded = vi.fn()
      renderUploadZone({ maxFiles: 3, filesCount: 3, onFilesAdded })

      fireEvent.drop(
        screen.getByLabelText('Justificatifs'),
        getDataTransfer([createFile()])
      )

      await new Promise((resolve) => setTimeout(resolve, 0))
      expect(onFilesAdded).not.toHaveBeenCalled()
    })
  })
})
