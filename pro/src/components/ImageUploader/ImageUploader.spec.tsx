import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { forwardRef } from 'react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ImageUploader, ImageUploaderProps } from './ImageUploader'

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
  '@/components/ImageUploader/components/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/validationSchema',
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
      initialValues: {
        croppedImageUrl: 'noimage.jpg',
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
    const mockFile = new File(['fake img'], 'fake_img.jpg', {})

    props = {
      onImageUpload: mockUpload,
      onImageDelete: async () => {},
    }

    renderImageUploader(props)

    await userEvent.click(screen.getByText('Ajouter une image'))

    expect(screen.getByText('Modifier une image')).toBeInTheDocument()
    expect(
      screen.getByText(
        'En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci.'
      )
    ).toBeInTheDocument()
    const inputField = screen.getByLabelText('Importez une image')
    await userEvent.upload(inputField, mockFile)

    await userEvent.click(screen.getByText('Importer'))

    expect(mockUpload).toHaveBeenCalled()
  })
})
