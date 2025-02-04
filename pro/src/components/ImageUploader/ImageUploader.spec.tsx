import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { forwardRef } from 'react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { ImageUploaderProps, ImageUploader } from './ImageUploader'
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
  'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/validationSchema',
  () => ({ getValidationSchema: () => ({ validate: vi.fn() }) })
)

const renderImageUploader = (props: ImageUploaderProps) =>
  renderWithProviders(<ImageUploader {...props} />)

describe('ImageUploader', () => {
  let props: ImageUploaderProps

  beforeEach(() => {
    props = {
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
    }
  })

  it('should render image uploader for existing file', () => {
    renderImageUploader(props)
    expect(
      screen.getByAltText('Prévisualisation de l’image')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Modifier/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Prévisualiser/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Supprimer/i })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: /Ajouter une image/i })
    ).not.toBeInTheDocument()
  })

  it('should render image uploader without file', () => {
    props = {
      onImageUpload: async () => {},
      onImageDelete: async () => {},
      mode: UploaderModeEnum.OFFER,
    }
    renderImageUploader(props)
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

    expect(
      screen.getByRole('button', { name: /Ajouter une image/i })
    ).toBeInTheDocument()
  })

  it('should upload a new image', async () => {
    const mockUpload = vi.fn()
    const mockFile = new File(['fake img'], 'fake_img.jpg', {
      type: 'image/jpeg',
    })

    props = {
      onImageUpload: mockUpload,
      onImageDelete: async () => {},
      mode: UploaderModeEnum.OFFER,
    }
    renderImageUploader(props)

    await userEvent.click(screen.getByText('Ajouter une image'))

    // dialog: import img
    const inputField = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )
    await userEvent.upload(inputField, mockFile)

    // dialog: crop img
    expect(screen.getByText('Modifier une image')).toBeInTheDocument()
    expect(
      screen.getByText(
        'En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci.'
      )
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Suivant'))

    // dialog: img preview
    expect(
      screen.getByText(
        'Prévisualisation de votre image dans l’application pass Culture'
      )
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Enregistrer'))

    expect(mockUpload).toHaveBeenCalled()
  })
})
