import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React, { forwardRef } from 'react'

import * as imageUtils from '@/commons/utils/image'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  ModalImageUpsertOrEdit,
  type ModalImageUpsertOrEditProps,
} from './ModalImageUpsertOrEdit'

const onImageUpload = vi.fn()
const onImageDelete = vi.fn()

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
    return React.createElement('div', { 'aria-label': "Editeur d'image" })
  })

  MockAvatarEditor.displayName = 'MockAvatarEditor'

  return {
    __esModule: true,
    default: MockAvatarEditor,
  }
})

const defaultProps: ModalImageUpsertOrEditProps = {
  open: true,
  mode: UploaderModeEnum.OFFER,
  onImageUpload,
  onImageDelete,
  initialValues: {
    draftImage: new File(['content'], 'draftImage.png', { type: 'image/png' }),
  },
}

const waitForRender = async () => {
  await waitFor(() => {
    expect(
      screen.getByRole('heading', { name: 'Modifier une image' })
    ).toBeInTheDocument()
  })
}

type ModalImageUpsertOrEditTestProps = Partial<ModalImageUpsertOrEditProps>
const renderModalImageCrop = (props: ModalImageUpsertOrEditTestProps = {}) => {
  const finalProps = {
    ...defaultProps,
    ...props,
  }

  return renderWithProviders(<ModalImageUpsertOrEdit {...finalProps} />)
}

describe('ModalImageUpsertOrEdit', () => {
  beforeEach(() => {
    fetchMock.mockResponse((request) => {
      if (
        request.url === 'http://example.com/image.jpg' &&
        request.method === 'GET'
      ) {
        return {
          status: 200,
          body: 'Mock Image Data',
          headers: { 'Content-Type': 'image/jpeg' },
        }
      }

      return { status: 404 }
    })
  })

  it('should render a cancel and a save button', async () => {
    renderModalImageCrop()
    await waitForRender()

    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Importer' })).toBeInTheDocument()
  })

  it('should render a spinner until the image is loaded', async () => {
    const mockImageUrl = 'http://example.com/image.jpg'
    renderModalImageCrop({
      initialValues: {
        croppedImageUrl: mockImageUrl,
        originalImageUrl: mockImageUrl,
      },
    })
    await waitFor(() => {
      expect(screen.getByTestId('spinner-img-load')).toBeInTheDocument()
    })
  })

  describe('when an image is loaded', () => {
    it('should render an image editor & a preview with the loaded image', async () => {
      vi.spyOn(imageUtils, 'getImageBitmap').mockResolvedValue({
        width: 500,
        height: 600,
      } as ImageBitmap)

      const mockImageUrl = 'http://example.com/image.jpg'
      renderModalImageCrop({
        initialValues: {
          croppedImageUrl: mockImageUrl,
          originalImageUrl: mockImageUrl,
        },
      })
      await waitForRender()

      expect(screen.getByLabelText("Editeur d'image")).toBeInTheDocument()
      expect(screen.getByText('Page d’accueil')).toBeInTheDocument()
      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(
        screen.queryByText(/La qualité de votre image n’est pas optimale./)
      ).not.toBeInTheDocument()
    })

    it('should display replace and delete buttons', async () => {
      const mockImageUrl = 'http://example.com/image.jpg'
      renderModalImageCrop({
        initialValues: {
          croppedImageUrl: mockImageUrl,
          originalImageUrl: mockImageUrl,
        },
      })
      await waitForRender()

      expect(
        screen.getByRole('button', { name: 'Remplacer l’image' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Supprimer l’image' })
      ).toBeInTheDocument()
    })

    it('should control change of the credit input', async () => {
      const mockImageUrl = 'http://example.com/image.jpg'
      renderModalImageCrop({
        initialValues: {
          croppedImageUrl: mockImageUrl,
          originalImageUrl: mockImageUrl,
        },
      })
      await waitForRender()

      const creditInput = screen.getByLabelText('Crédit de l’image')
      expect(creditInput).toBeInTheDocument()

      await userEvent.type(creditInput, 'John Doe')

      expect(creditInput).toHaveValue('John Doe')
    })

    describe('when the image has small dimensions', () => {
      it('should not display any warning message for venues', async () => {
        vi.spyOn(imageUtils, 'getImageBitmap').mockResolvedValue({
          width: 10,
          height: 10,
        } as ImageBitmap)

        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
          mode: UploaderModeEnum.VENUE,
        })
        await waitForRender()
        expect(
          screen.queryByText(/La qualité de votre image n’est pas optimale./)
        ).not.toBeInTheDocument()
      })

      it('should not display any warning message for collective offers', async () => {
        vi.spyOn(imageUtils, 'getImageBitmap').mockResolvedValue({
          width: 10,
          height: 10,
        } as ImageBitmap)

        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
          mode: UploaderModeEnum.OFFER_COLLECTIVE,
        })
        await waitForRender()
        expect(
          screen.queryByText(/La qualité de votre image n’est pas optimale./)
        ).not.toBeInTheDocument()
      })

      it('should display a warning message for individual offers', async () => {
        vi.spyOn(imageUtils, 'getImageBitmap').mockResolvedValue({
          width: 10,
          height: 10,
        } as ImageBitmap)

        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
          mode: UploaderModeEnum.OFFER,
        })
        await waitForRender()
        expect(
          screen.getByText(/Image non conforme aux recommandations/)
        ).toBeInTheDocument()
      })
    })

    describe('when the replace button is clicked', () => {
      it('should render the image drag and drop component', async () => {
        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
        })
        await waitForRender()

        const replaceButton = screen.getByRole('button', {
          name: 'Remplacer l’image',
        })
        await userEvent.click(replaceButton)

        expect(screen.getByLabelText('Importez une image')).toBeInTheDocument()
        expect(
          screen.queryByLabelText("Editeur d'image")
        ).not.toBeInTheDocument()
      })

      it('should disable the save button', async () => {
        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
        })
        await waitForRender()

        const replaceButton = screen.getByRole('button', {
          name: 'Remplacer l’image',
        })
        await userEvent.click(replaceButton)

        expect(screen.getByRole('button', { name: 'Importer' })).toBeDisabled()
      })

      it('should display the image editor again once the image is uploaded', async () => {
        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
        })
        await waitForRender()

        const replaceButton = screen.getByRole('button', {
          name: 'Remplacer l’image',
        })
        await userEvent.click(replaceButton)

        const imageFile = new File(['content'], 'image.png', {
          type: 'image/png',
        })
        await userEvent.upload(screen.getByLabelText('Importez une image'), [
          imageFile,
        ])

        expect(screen.getByLabelText("Editeur d'image")).toBeInTheDocument()
        expect(
          screen.queryByLabelText('Importez une image')
        ).not.toBeInTheDocument()
      })
    })

    describe('when the delete button is clicked', () => {
      it('should call onImageDelete', async () => {
        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
        })
        await waitForRender()

        const deleteButton = screen.getByRole('button', {
          name: 'Supprimer l’image',
        })
        await userEvent.click(deleteButton)

        expect(onImageDelete).toHaveBeenCalled()
      })
    })

    describe('when saving an image', () => {
      it('should call onImageUpload with sucess message : Votre image a bien été importée', async () => {
        renderModalImageCrop()

        await waitForRender()

        const saveButton = screen.getByRole('button', { name: 'Importer' })
        await userEvent.click(saveButton)

        await waitFor(() => {
          expect(onImageUpload).toHaveBeenCalled()
        })

        expect(onImageUpload).toHaveBeenCalledWith(
          expect.objectContaining({
            imageFile: expect.any(File),
            imageCroppedDataUrl: expect.any(String),
            cropParams: expect.any(Object),
            credit: expect.any(String),
          }),
          'Votre image a bien été importée'
        )
      })

      it('should call onImageUpload with success message : Vos modifications ont bien été prises en compte', async () => {
        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
        })

        await waitForRender()

        const saveButton = screen.getByRole('button', { name: 'Importer' })
        await userEvent.click(saveButton)

        expect(onImageUpload).toHaveBeenCalledOnce()

        expect(onImageUpload).toHaveBeenCalledWith(
          expect.objectContaining({
            imageFile: expect.any(File),
            imageCroppedDataUrl: expect.any(String),
            cropParams: expect.any(Object),
            credit: expect.any(String),
          }),
          'Vos modifications ont bien été prises en compte'
        )
      })
    })

    describe('when it is used in COLLECTIVE OFFER mode', () => {
      it('should not display the preview', async () => {
        const mockImageUrl = 'http://example.com/image.jpg'
        renderModalImageCrop({
          initialValues: {
            croppedImageUrl: mockImageUrl,
            originalImageUrl: mockImageUrl,
          },
          mode: UploaderModeEnum.OFFER_COLLECTIVE,
        })
        await waitForRender()

        expect(screen.queryByText('Page d’accueil')).not.toBeInTheDocument()
        expect(screen.queryByText('Détails de l’offre')).not.toBeInTheDocument()
      })
    })
  })
})
