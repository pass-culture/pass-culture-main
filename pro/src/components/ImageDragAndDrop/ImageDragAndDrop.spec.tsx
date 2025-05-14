import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import { ImageDragAndDrop } from './ImageDragAndDrop'

function mockData(files: File[]) {
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

const createObjectURLMock = vi.fn(() => 'mocked-url')
const revokeObjectURLMock = vi.fn()
vi.stubGlobal('URL', {
  createObjectURL: createObjectURLMock,
  revokeObjectURL: revokeObjectURLMock,
})

describe('ImageDragAndDrop', () => {
  it('should render the component with a drop zone and an input', () => {
    const { container } = render(<ImageDragAndDrop />)

    expect(container).toBeInTheDocument()
    const dragAndDrop = screen.getByTestId('image-drag-and-drop')
    expect(dragAndDrop).toBeInTheDocument()

    const input = screen.getByLabelText(
      /Importez une image/
    ) as HTMLInputElement
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('type', 'file')
    expect(input).toHaveAttribute(
      'accept',
      'image/jpeg,.jpeg,.jpg,image/png,.png,image/mpo,.mpo,image/webp,.webp'
    )
  })

  it('should display the correct text when dragging over', async () => {
    const file = new File(['test'], 'test-image.jpg', { type: 'image/jpeg' })
    const data = mockData([file])

    render(<ImageDragAndDrop />)

    fireEvent.dragEnter(screen.getByTestId('image-drag-and-drop'), data)
    await waitFor(() => {
      expect(screen.getByText(/Déposez votre image ici/)).toBeInTheDocument()
    })

    expect(
      screen.queryByText(/Glissez et déposez votre image ou/)
    ).not.toBeInTheDocument()
    expect(screen.queryByText(/Importez une image/)).not.toBeInTheDocument()
  })

  it('should call onDropOrSelected when a valid file is dropped', async () => {
    const file = new File(['test'], 'test-image.jpg', { type: 'image/jpeg' })
    const data = mockData([file])

    const onDropOrSelected = vi.fn()
    render(<ImageDragAndDrop onDropOrSelected={onDropOrSelected} />)

    fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

    await waitFor(() => {
      expect(onDropOrSelected).toHaveBeenCalledWith(file)
    })
  })

  it('should display the appropriate err message when an invalid file type is dropped & call onError', async () => {
    const file = new File(['test'], 'test-image.txt', { type: 'txt' })
    const data = mockData([file])

    const onError = vi.fn()
    render(<ImageDragAndDrop onError={onError} />)

    fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        /Le format de l’image n’est pas valide/
      )
    })

    expect(onError).toHaveBeenCalledWith(['file-invalid-type'])
  })

  it('should display the appropriate err message when the file is too large & call onError', async () => {
    const file = new File(['test'], 'test-image.jpg', { type: 'image/jpeg' })
    Object.defineProperty(file, 'size', { value: 11 * 1024 * 1024 })
    const data = mockData([file])

    const onError = vi.fn()
    render(<ImageDragAndDrop onError={onError} />)

    fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        /Le poids du fichier est trop lourd/
      )
    })

    expect(onError).toHaveBeenCalledWith(['file-too-large'])
  })

  describe('when dimension constraints are provided', () => {
    it('should display them above the drop zone', () => {
      render(
        <ImageDragAndDrop
          minSizes={{
            width: 100,
            height: 400,
          }}
        />
      )

      expect(screen.getByText(/Hauteur minimum :/)).toBeInTheDocument()
      expect(screen.getByText(/Largeur minimum :/)).toBeInTheDocument()
    })

    it('should display the appropriate error message when the image has invalid dimensions', async () => {
      const file = new File(['test'], 'test-image.jpg', { type: 'image/jpeg' })
      const data = mockData([file])
      global.Image = class {
        width = 10
        height = 10
        onload: (() => void) | null = null

        set src(val: string) {
          this._src = val
          setTimeout(() => this.onload?.(), 0)
        }

        get src() {
          return this._src
        }

        private _src = ''
      } as unknown as typeof Image

      const onError = vi.fn()
      render(
        <ImageDragAndDrop
          minSizes={{
            width: 400,
            height: 600,
          }}
          onError={onError}
        />
      )

      fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          /L’image doit faire au moins/
        )
      })

      expect(onError).toHaveBeenCalledWith([
        'file-invalid-dimensions-width',
        'file-invalid-dimensions-height',
      ])
    })
  })
})
