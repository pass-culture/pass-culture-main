import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { forwardRef } from 'react'

import * as useNotification from 'commons/hooks/useNotification'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  ImageDragAndDropUploader,
  ImageDragAndDropUploaderProps,
} from './ImageDragAndDropUploader'
import { UploaderModeEnum } from './types'

vi.mock('react-avatar-editor', () => {
  const MockAvatarEditor = forwardRef((props, ref) => {
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

  return {
    __esModule: true,
    default: MockAvatarEditor,
  }
})

vi.mock(
  'components/ImageUploader/components/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/validationSchema',
  () => ({ getValidationSchema: () => ({ validate: vi.fn() }) })
)

const renderImageUploader = (props: ImageDragAndDropUploaderProps) =>
  renderWithProviders(<ImageDragAndDropUploader {...props} />)

describe('ImageDragAndDropUploader', () => {
  it('should render image uploader for existing file', () => {
    renderImageUploader({
      onImageUpload: async () => {},
      onImageDelete: async () => {},
      mode: UploaderModeEnum.OFFER,
      initialValues: {
        imageUrl: 'noimage.jpg',
        originalImageUrl: 'noimage.jpg',
        credit: 'John Do',
        cropParams: {
          xCropPercent: 100,
          yCropPercent: 100,
          heightCropPercent: 1,
          widthCropPercent: 1,
        },
      },
    })

    expect(
      screen.getByAltText('Prévisualisation de l’image')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Modifier/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Supprimer/i })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: /Ajouter une image/i })
    ).not.toBeInTheDocument()
  })

  it('should render image uploader without file', () => {
    renderImageUploader({
      onImageUpload: async () => {},
      onImageDelete: async () => {},
      mode: UploaderModeEnum.OFFER,
    })

    expect(
      screen.queryByAltText('Prévisualisation de l’image')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /Modifier/i })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /Prévisualiser/i })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /Supprimer/i })
    ).not.toBeInTheDocument()
    expect(screen.getByLabelText('Importez une image')).toBeInTheDocument()
  })

  it('should upload a new image', async () => {
    const mockUpload = vi.fn()
    const mockNotifySuccess = vi.fn()
    const mockFile = new File(['fake img'], 'fake_img.jpg', {
      type: 'image/jpeg',
    })

    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      success: mockNotifySuccess,
    }))

    renderImageUploader({
      onImageUpload: mockUpload,
      onImageDelete: async () => {},
      mode: UploaderModeEnum.OFFER,
    })

    const inputField = screen.getByLabelText('Importez une image')
    await userEvent.upload(inputField, mockFile)

    // dialog: crop img
    expect(screen.getByText('Modifier une image')).toBeInTheDocument()
    expect(
      screen.getByText(
        'En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci.'
      )
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Enregistrer'))

    expect(mockUpload).toHaveBeenCalled()
    expect(mockNotifySuccess).toHaveBeenCalledWith(
      'Votre image a bien été enregistrée'
    )
  })

  it('should delete an image', async () => {
    const mockDelete = vi.fn()
    const mockNotifySuccess = vi.fn()

    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      success: mockNotifySuccess,
    }))

    renderImageUploader({
      onImageUpload: async () => {},
      onImageDelete: mockDelete,
      mode: UploaderModeEnum.OFFER,
      initialValues: {
        imageUrl: 'noimage.jpg',
        originalImageUrl: 'noimage.jpg',
        credit: 'John Do',
        cropParams: {
          xCropPercent: 100,
          yCropPercent: 100,
          heightCropPercent: 1,
          widthCropPercent: 1,
        },
      },
    })

    await userEvent.click(screen.getByRole('button', { name: /Supprimer/i }))
    expect(mockDelete).toHaveBeenCalled()
    expect(mockNotifySuccess).toHaveBeenCalledWith(
      'L’image a bien été supprimée'
    )
  })
})
