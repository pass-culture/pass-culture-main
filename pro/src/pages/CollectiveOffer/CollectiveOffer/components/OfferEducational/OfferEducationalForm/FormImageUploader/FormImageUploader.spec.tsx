import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { forwardRef, useState } from 'react'
import { axe } from 'vitest-axe'

import type { OfferCollectiveImage } from '@/commons/core/Offers/types'
import { imageFileFactory } from '@/commons/utils/factories/imageUploadArgsFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  FormImageUploader,
  type ImageUploaderOfferProps,
} from './FormImageUploader'

const snackBarSuccess = vi.fn()
const snackBarError = vi.fn()

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => ({
    success: snackBarSuccess,
    error: snackBarError,
  }),
}))

vi.mock('@/commons/utils/imageUpload/getImageDimensions', () => ({
  getImageDimensions: vi.fn((file) =>
    Promise.resolve({
      width: (file as any).width || 0,
      height: (file as any).height || 0,
    })
  ),
}))

vi.mock('react-avatar-editor', () => {
  const MockAvatarEditor = forwardRef((_props, ref) => {
    if (ref && typeof ref === 'object' && 'current' in ref) {
      ref.current = {
        getImage: vi.fn(() => ({ toDataURL: vi.fn(() => 'my img') })),
        getCroppingRect: vi.fn(() => ({
          x: 0,
          y: 0,
          width: 100,
          height: 100,
        })),
      }
    }
    return ''
  })
  MockAvatarEditor.displayName = 'MockAvatarEditor'
  return { __esModule: true, default: MockAvatarEditor }
})

const IMAGE_INPUT_LABEL = 'Importez ou déposez le fichier ici'

const imageOffer: OfferCollectiveImage = {
  url: 'https://example.com/image.jpg',
  credit: 'John Do',
  alternativeText: '',
}

const createImage = ({ width = 400, height = 600 } = {}) =>
  Object.assign(imageFileFactory('image.jpg'), { width, height })

const renderFormImageUploader = (
  props: Partial<ImageUploaderOfferProps> = {}
) =>
  renderWithProviders(
    <FormImageUploader
      onImageUpload={vi.fn()}
      onImageDelete={vi.fn()}
      imageOffer={null}
      disableForm={false}
      isTemplate={false}
      {...props}
    />
  )

describe('FormImageUploader', () => {
  beforeEach(() => {
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderFormImageUploader()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should describe the upload zone with the minimum dimensions of the image', () => {
    renderFormImageUploader()

    const input = screen.getByLabelText(IMAGE_INPUT_LABEL)
    expect(input).toHaveAttribute('type', 'file')
    expect(input).toHaveAccessibleDescription(
      /Résolution maximale : 80 mégapixels\. Largeur minimale : 400 px\. Hauteur minimale : 600 px\.$/
    )
  })

  it('should display the image preview and its actions when the offer has an image', () => {
    renderFormImageUploader({ imageOffer })

    expect(screen.getByAltText('Prévisualisation de l’image')).toHaveAttribute(
      'src',
      imageOffer.url
    )
    expect(
      screen.getByRole('button', { name: 'Modifier l’image' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Supprimer' })
    ).toBeInTheDocument()
    expect(screen.queryByLabelText(IMAGE_INPUT_LABEL)).not.toBeInTheDocument()
  })

  it('should clear the displayed credit when the image credit is cleared', () => {
    const { rerender } = renderFormImageUploader({ imageOffer })

    expect(screen.getByText('Crédit image : John Do')).toBeVisible()

    rerender(
      <FormImageUploader
        onImageUpload={vi.fn()}
        onImageDelete={vi.fn()}
        imageOffer={{ url: 'https://example.com/new-image.jpg', credit: '' }}
        disableForm={false}
        isTemplate={false}
      />
    )

    expect(screen.getByAltText('Prévisualisation de l’image')).toHaveAttribute(
      'src',
      'https://example.com/new-image.jpg'
    )
    expect(screen.queryByText(/Crédit image :/)).not.toBeInTheDocument()
  })

  it.each([
    {
      case: 'too narrow',
      file: createImage({ width: 399 }),
      message:
        'L’image doit faire au moins 400 pixels de large et 600 pixels de haut',
    },
    {
      case: 'too short',
      file: createImage({ height: 599 }),
      message:
        'L’image doit faire au moins 400 pixels de large et 600 pixels de haut',
    },
    {
      case: 'not an image',
      file: new File(['not an image'], 'image.jpg', { type: 'image/jpeg' }),
      message: 'Le format de l’image n’est pas valide',
    },
  ])(
    'should display an error when the image is $case',
    async ({ file, message }) => {
      const user = userEvent.setup()
      const onImageDropOrSelected = vi.fn()
      renderFormImageUploader({ onImageDropOrSelected })
      const input = screen.getByLabelText(IMAGE_INPUT_LABEL)

      await user.upload(input, file)

      await waitFor(() => {
        expect(input).toHaveAccessibleDescription(
          expect.stringContaining(message)
        )
      })
      expect(input).toBeInvalid()
      expect(input).toHaveFocus()
      expect(
        screen.queryByLabelText('Crédit de l’image')
      ).not.toBeInTheDocument()
      expect(onImageDropOrSelected).not.toHaveBeenCalled()
    }
  )

  it('should replace the error of a previous image when a new file is rejected', async () => {
    const user = userEvent.setup({ applyAccept: false })
    renderFormImageUploader()
    const input = screen.getByLabelText(IMAGE_INPUT_LABEL)

    await user.upload(input, createImage({ width: 399 }))
    await waitFor(() => {
      expect(input).toHaveAccessibleDescription(
        expect.stringContaining('L’image doit faire au moins')
      )
    })

    await user.upload(
      input,
      new File(['%PDF'], 'document.pdf', { type: 'application/pdf' })
    )

    // The errors of the files rejected by the zone are part of the input name.
    await waitFor(() => {
      expect(input).toHaveAccessibleName(
        expect.stringContaining('Le format du fichier n’est pas accepté.')
      )
    })
    expect(input).not.toHaveAccessibleDescription(
      expect.stringContaining('L’image doit faire au moins')
    )
    expect(
      screen.queryByText(/^L’image doit faire au moins/)
    ).not.toBeInTheDocument()
  })

  it('should import the image edited in the modal', async () => {
    const user = userEvent.setup()
    const onImageUpload = vi.fn()
    const onImageDropOrSelected = vi.fn()
    renderFormImageUploader({ onImageUpload, onImageDropOrSelected })

    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), createImage())

    expect(
      await screen.findByRole('heading', { name: 'Modifier une image' })
    ).toBeInTheDocument()
    expect(onImageDropOrSelected).toHaveBeenCalledTimes(1)

    await user.click(screen.getByRole('button', { name: 'Importer' }))

    expect(onImageUpload).toHaveBeenCalledWith(
      expect.objectContaining({
        imageFile: expect.any(File),
        imageCroppedDataUrl: 'my img',
      })
    )
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Votre image a bien été importée',
      expect.any(String)
    )
    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: 'Modifier une image' })
      ).not.toBeInTheDocument()
    })
  })

  it('should notify an error when the image import fails', async () => {
    const user = userEvent.setup()
    renderFormImageUploader({
      onImageUpload: () => {
        throw new Error('Upload failed')
      },
    })

    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), createImage())
    await user.click(await screen.findByRole('button', { name: 'Importer' }))

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        "Une erreur est survenue lors de l'importation de votre image",
        expect.any(String)
      )
    })
    expect(snackBarSuccess).not.toHaveBeenCalled()
  })

  it('should focus the upload zone back and accept a new image when the image modal is cancelled', async () => {
    const user = userEvent.setup()
    renderFormImageUploader()
    const image = createImage()

    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), image)
    await user.click(await screen.findByRole('button', { name: 'Annuler' }))

    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: 'Modifier une image' })
      ).not.toBeInTheDocument()
      expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toHaveFocus()
    })

    // Uploading the same file again validates that the upload zone was remounted.
    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), image)

    expect(
      await screen.findByRole('heading', { name: 'Modifier une image' })
    ).toBeInTheDocument()
  })

  it('should reuse the original file when editing an imported image after cancelling', async () => {
    const user = userEvent.setup()
    const onImageUpload = vi.fn()

    // The "Modifier" button only shows once the parent displays the imported image
    const StatefulFormImageUploader = () => {
      const [statefulImageOffer, setStatefulImageOffer] =
        useState<OfferCollectiveImage | null>(null)

      return (
        <FormImageUploader
          onImageUpload={(values) => {
            onImageUpload(values)
            setStatefulImageOffer({ url: values.imageCroppedDataUrl })
          }}
          onImageDelete={vi.fn()}
          imageOffer={statefulImageOffer}
          disableForm={false}
          isTemplate={false}
        />
      )
    }

    renderWithProviders(<StatefulFormImageUploader />)

    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), createImage())
    await user.click(await screen.findByRole('button', { name: 'Importer' }))

    // Reopen the editor, then close it without importing.
    await user.click(screen.getByRole('button', { name: 'Modifier l’image' }))
    await user.click(await screen.findByRole('button', { name: 'Annuler' }))

    await user.click(screen.getByRole('button', { name: 'Modifier l’image' }))
    await user.click(await screen.findByRole('button', { name: 'Importer' }))

    await waitFor(() => {
      expect(onImageUpload).toHaveBeenCalledTimes(2)
    })
    expect(fetchMock).not.toHaveBeenCalledWith('my img')
    const originalFile = onImageUpload.mock.calls[0][0].imageFile
    expect(onImageUpload.mock.calls[1][0].imageFile).toBe(originalFile)
  })

  it('should delete the image', async () => {
    const user = userEvent.setup()
    const onImageDelete = vi.fn()
    renderFormImageUploader({ imageOffer, onImageDelete })

    await user.click(screen.getByRole('button', { name: 'Supprimer' }))

    expect(onImageDelete).toHaveBeenCalledTimes(1)
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'L’image a bien été supprimée',
      expect.any(String)
    )
  })

  it('should disable the upload zone when the form is disabled', () => {
    renderFormImageUploader({ disableForm: true })

    expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeDisabled()
  })
})
