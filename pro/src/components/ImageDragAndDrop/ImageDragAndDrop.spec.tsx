import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import { imageFileFactory } from '@/commons/utils/factories/imageUploadArgsFactories'

import { MAX_FILE_SIZE } from './constants'
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

vi.mock('./getImageDimensions', () => ({
  getImageDimensions: vi.fn((file) => {
    return Promise.resolve({
      width: (file as any).width || 0,
      height: (file as any).height || 0,
    })
  }),
}))

describe('ImageDragAndDrop', () => {
  it('should render the component with a drop zone and an input', () => {
    render(<ImageDragAndDrop />)

    const dragAndDrop = screen.getByTestId('image-drag-and-drop')
    expect(dragAndDrop).toBeInTheDocument()

    const input = screen.getByTestId('file-input')
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('type', 'file')
    expect(input).toHaveAccessibleDescription(
      /Formats acceptés.*JPG, JPEG, PNG, mpo, webP.*Poids maximal du fichier.*10 Mo.*Résolution maximale de l’image.*80 Mégapixels/
    )
    expect(screen.getByRole('list').children).toHaveLength(3)
    expect(input).toHaveAttribute(
      'accept',
      'image/jpeg,.jpeg,.jpg,image/png,.png,image/mpo,.mpo,image/webp,.webp'
    )
  })

  it('should display the correct text when dragging over', async () => {
    const file = Object.assign(imageFileFactory(), {
      width: 800,
      height: 600,
    })
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
    const file = Object.assign(imageFileFactory(), {
      width: 800,
      height: 600,
    })
    const data = mockData([file])

    const onDropOrSelected = vi.fn()
    render(<ImageDragAndDrop onDropOrSelected={onDropOrSelected} />)

    fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

    await waitFor(() => {
      expect(onDropOrSelected).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'test-image.jpg',
          type: 'image/jpeg',
          width: 800,
          height: 600,
        })
      )
    })
    expect(screen.getByTestId('file-input')).toHaveAccessibleDescription(
      /Formats acceptés.*JPG, JPEG, PNG, mpo, webP.*Poids maximal du fichier.*10 Mo.*Résolution maximale de l’image.*80 Mégapixels/
    )
  })

  it('should display the appropriate err message when an invalid file type is dropped & call onError', async () => {
    const file = Object.assign(
      new File(['test'], 'test-image.txt', { type: 'txt' }),
      {
        width: 800,
        height: 600,
      }
    )
    const data = mockData([file])

    const onError = vi.fn()
    render(<ImageDragAndDrop onError={onError} />)
    const input = screen.getByTestId('file-input')

    fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

    await waitFor(() => {
      expect(screen.getAllByRole('alert', { hidden: true })).toHaveLength(1)
      expect(screen.getByRole('alert', { hidden: true })).toHaveAttribute(
        'aria-hidden',
        'true'
      )
      expect(screen.getByRole('alert', { hidden: true })).toHaveTextContent(
        'Le format de l’image n’est pas valide'
      )
      expect(input).toHaveAccessibleDescription(
        'Le format de l’image n’est pas valide'
      )
      expect(screen.getByRole('list').children).toHaveLength(3)
      expect(
        screen.getByRole('alert', { hidden: true }).closest('ul')
      ).toBeNull()
      expect(
        screen.getByRole('img', { name: 'Critère non respecté' })
      ).toBeInTheDocument()
    })

    expect(onError).toHaveBeenCalledWith(['file-invalid-type'])
  })

  it('should display the appropriate err message when the file is too large & call onError', async () => {
    const file = Object.assign(imageFileFactory(), {
      width: 800,
      height: 600,
    })
    Object.defineProperty(file, 'size', { value: MAX_FILE_SIZE + 1 })
    const data = mockData([file])

    const onError = vi.fn()
    render(<ImageDragAndDrop onError={onError} />)

    fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

    await waitFor(() => {
      expect(screen.getAllByRole('alert', { hidden: true })).toHaveLength(1)
      expect(screen.getByRole('alert', { hidden: true })).toHaveTextContent(
        'Le poids du fichier est trop lourd'
      )
      expect(screen.getByTestId('file-input')).toHaveAccessibleDescription(
        'Le poids du fichier est trop lourd'
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

    it('should display the appropriate error message when the image has too short dimensions', async () => {
      const file = Object.assign(imageFileFactory(), {
        width: 10,
        height: 10,
      })

      const data = mockData([file])

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
        expect(screen.getAllByRole('alert', { hidden: true })).toHaveLength(2)
        expect(
          screen.getByText('L’image doit faire au moins 600 pixels de haut')
        ).toBeInTheDocument()
        expect(
          screen.getByText('L’image doit faire au moins 400 pixels de large')
        ).toBeInTheDocument()
      })

      expect(onError).toHaveBeenCalledWith([
        'file-invalid-dimensions-width',
        'file-invalid-dimensions-height',
      ])
    })

    it('should display the appropriate error message when the image has too large dimensions', async () => {
      const file = Object.assign(imageFileFactory(), {
        width: 81,
        height: 1_000_000,
      })

      const data = mockData([file])

      const onError = vi.fn()
      render(<ImageDragAndDrop onError={onError} />)

      fireEvent.drop(screen.getByTestId('image-drag-and-drop'), data)

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(['file-too-large-dimensions'])
      })
    })
  })
})
