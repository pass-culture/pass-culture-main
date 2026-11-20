import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { forwardRef } from 'react'

import { api } from '@/apiClient/api'
import * as apiHelpers from '@/apiClient/helpers'
import {
  DisplayableActivity,
  type GetVenueResponseModel,
  VenueState,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { DisplayableActivityMap } from '@/commons/mappings/DisplayableActivity'
import { imageFileFactory } from '@/commons/utils/factories/imageUploadArgsFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Header, type HeaderProps } from './Header'

const bannerMeta = {
  image_credit: null,
  original_image_url: 'https://www.example.com/image.png',
  crop_params: {
    x_crop_percent: 0,
    y_crop_percent: 0,
    width_crop_percent: 0,
    height_crop_percent: 0,
  },
}

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
    return <div data-testid="mock-avatar-editor" />
  })
  MockAvatarEditor.displayName = 'MockAvatarEditor'
  return { __esModule: true, default: MockAvatarEditor }
})

vi.mock('@/apiClient/helpers', () => ({
  getFileFromURL: vi.fn(),
}))

const mockMutate = vi.fn()
vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: vi.fn(() => ({ mutate: mockMutate })),
}))

const mockUseOnVenueImageUpload = vi.hoisted(() => vi.fn())
vi.mock('@/commons/core/Venue/hooks/useOnVenueImageUpload', () => ({
  useOnVenueImageUpload: mockUseOnVenueImageUpload,
}))

const snackBarSuccess = vi.fn()
const snackBarError = vi.fn()

const IMAGE_INPUT_LABEL = 'Importez ou déposez le fichier ici'

const renderHeader = (
  context: HeaderProps['context'] = 'partnerPage',
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<Header context={context} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          ...venueOverrides,
        }),
      },
    },
  })

describe('Header', () => {
  beforeEach(() => {
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    mockUseOnVenueImageUpload.mockReturnValue({
      imageValues: {},
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn(),
    })
    // Same object on every render: the image edition modal depends on it.
    vi.spyOn(useSnackBar, 'useSnackBar').mockReturnValue({
      success: snackBarSuccess,
      error: snackBarError,
    })
  })

  it('should display the venue public name and activity label', () => {
    renderHeader('partnerPage', { activity: DisplayableActivity.FESTIVAL })

    expect(screen.getByText('Nom public de la structure 1')).toBeInTheDocument()
    expect(
      screen.getByText(DisplayableActivityMap.get('FESTIVAL') ?? '')
    ).toBeInTheDocument()
  })

  it('should not display any activity label when the venue has no activity', () => {
    renderHeader('partnerPage', { activity: null })

    expect(
      screen.queryByText(DisplayableActivityMap.get('OTHER') ?? '')
    ).not.toBeInTheDocument()
  })

  it('should display the image uploader when there is no image', () => {
    renderHeader('partnerPage')

    expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeInTheDocument()
  })

  it('should log an event on image upload', async () => {
    const user = userEvent.setup()
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const mockFile = Object.assign(imageFileFactory('fake_img.jpg'), {
      width: 100,
      height: 100,
    })

    renderHeader('partnerPage')

    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), mockFile)

    await waitFor(() => {
      expect(mockLogEvent).toHaveBeenCalledWith(Events.DRAG_OR_SELECTED_IMAGE, {
        imageType: UploaderModeEnum.VENUE,
        isEdition: true,
        imageCreationStage: 'add image',
      })
    })
  })

  it('should display an error and not open the image edition modal when the file is not an image', async () => {
    const user = userEvent.setup()
    renderHeader('partnerPage')
    const input = screen.getByLabelText(IMAGE_INPUT_LABEL)

    await user.upload(
      input,
      new File(['not an image'], 'fake_img.jpg', { type: 'image/jpeg' })
    )

    await waitFor(() => {
      expect(input).toHaveAccessibleDescription(
        expect.stringContaining('Le format de l’image n’est pas valide')
      )
    })
    expect(input).toBeInvalid()
    expect(input).toHaveFocus()
    expect(
      screen.queryByRole('heading', { name: 'Modifier une image' })
    ).not.toBeInTheDocument()
  })

  it('should upload the image imported through the image edition modal', async () => {
    const user = userEvent.setup()
    const handleOnImageUpload = vi.fn()
    mockUseOnVenueImageUpload.mockReturnValue({
      imageValues: {},
      setImageValues: vi.fn(),
      handleOnImageUpload,
    })

    renderHeader('partnerPage')

    await user.upload(
      screen.getByLabelText(IMAGE_INPUT_LABEL),
      Object.assign(imageFileFactory('fake_img.jpg'), {
        width: 100,
        height: 100,
      })
    )
    await user.click(await screen.findByRole('button', { name: 'Importer' }))

    expect(handleOnImageUpload).toHaveBeenCalledWith(
      expect.objectContaining({
        imageFile: expect.any(File),
        imageCroppedDataUrl: 'my img',
      })
    )
    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: 'Modifier une image' })
      ).not.toBeInTheDocument()
    })
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Votre image a bien été importée',
      expect.any(String)
    )
  })

  it('should notify an error when the image upload fails', async () => {
    const user = userEvent.setup()
    mockUseOnVenueImageUpload.mockReturnValue({
      imageValues: {},
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn().mockRejectedValue(new Error('Upload error')),
    })

    renderHeader('partnerPage')

    await user.upload(
      screen.getByLabelText(IMAGE_INPUT_LABEL),
      Object.assign(imageFileFactory('fake_img.jpg'), {
        width: 100,
        height: 100,
      })
    )
    await user.click(await screen.findByRole('button', { name: 'Importer' }))

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        "Une erreur est survenue lors de l'importation de votre image",
        expect.any(String)
      )
    })
    expect(snackBarSuccess).not.toHaveBeenCalled()
  })

  it('should only discard the image being imported when it is deleted from the image edition modal', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'deleteVenueBanner')

    renderHeader('partnerPage')

    await user.upload(
      screen.getByLabelText(IMAGE_INPUT_LABEL),
      Object.assign(imageFileFactory('fake_img.jpg'), {
        width: 100,
        height: 100,
      })
    )
    await user.click(
      await screen.findByRole('button', { name: 'Supprimer l’image' })
    )

    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: 'Modifier une image' })
      ).not.toBeInTheDocument()
    })
    expect(api.deleteVenueBanner).not.toHaveBeenCalled()
    expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeInTheDocument()
  })

  it('should display the preview link on the partner page', () => {
    renderHeader('partnerPage')

    expect(screen.getByText('Visualiser votre page')).toBeInTheDocument()
  })

  it('should not display the preview link in the collective context', () => {
    renderHeader('collective')

    expect(screen.queryByText('Visualiser votre page')).not.toBeInTheDocument()
  })

  it('should display the edit image button when an image is present', () => {
    mockUseOnVenueImageUpload.mockReturnValueOnce({
      imageValues: {
        croppedImageUrl: 'https://www.example.com/image.png',
        credit: '',
      },
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn(),
    })

    renderHeader('partnerPage', {
      bannerUrl: 'https://www.example.com/image.png',
      bannerMeta,
    })

    expect(screen.getByRole('button', { name: /Modifier/ })).toBeInTheDocument()
  })

  it('should enable the image uploader when the venue is open', () => {
    renderHeader('partnerPage', { state: null })

    expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeEnabled()
  })

  it('should disable the image uploader when the venue is closed', () => {
    renderHeader('partnerPage', { state: VenueState.CLOSED })

    expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeDisabled()
  })

  it('should not display the preview link when the venue is closed', () => {
    renderHeader('partnerPage', {
      state: VenueState.CLOSED,
    })

    expect(screen.queryByText('Visualiser votre page')).not.toBeInTheDocument()
  })

  it('should not display the edit image button when the venue is closed', () => {
    mockUseOnVenueImageUpload.mockReturnValueOnce({
      imageValues: {
        croppedImageUrl: 'https://www.example.com/image.png',
        credit: '',
      },
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn(),
    })

    renderHeader('partnerPage', {
      bannerUrl: 'https://www.example.com/image.png',
      bannerMeta,
      state: VenueState.CLOSED,
    })

    expect(
      screen.queryByRole('button', { name: 'Modifier l’image' })
    ).not.toBeInTheDocument()
  })

  it('should call the delete endpoint and notify success when deleting the image', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'deleteVenueBanner').mockResolvedValueOnce()
    vi.mocked(apiHelpers.getFileFromURL).mockResolvedValueOnce(
      new File([''], 'mocked_file.jpg', { type: 'image/jpeg' })
    )
    mockUseOnVenueImageUpload.mockReturnValueOnce({
      imageValues: {
        croppedImageUrl: 'https://www.example.com/image.png',
        credit: '',
      },
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn(),
    })

    renderHeader('partnerPage', {
      bannerUrl: 'https://www.example.com/image.png',
      bannerMeta,
    })

    await user.click(screen.getByRole('button', { name: /Modifier/ }))
    await user.click(await screen.findByRole('button', { name: /Supprimer/ }))

    expect(api.deleteVenueBanner).toHaveBeenCalledWith({
      path: { venue_id: 1 },
    })
    await waitFor(() => {
      expect(snackBarSuccess).toHaveBeenCalledWith(
        'Votre image a bien été supprimée',
        expect.any(String)
      )
    })
  })

  it('should notify an error when image deletion fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'deleteVenueBanner').mockRejectedValueOnce('Deletion error')
    vi.mocked(apiHelpers.getFileFromURL).mockResolvedValueOnce(
      new File([''], 'mocked_file.jpg', { type: 'image/jpeg' })
    )
    mockUseOnVenueImageUpload.mockReturnValueOnce({
      imageValues: {
        croppedImageUrl: 'https://www.example.com/image.png',
        credit: '',
      },
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn(),
    })

    renderHeader('partnerPage', {
      bannerUrl: 'https://www.example.com/image.png',
      bannerMeta,
    })

    await user.click(screen.getByRole('button', { name: /Modifier/ }))
    await user.click(await screen.findByRole('button', { name: /Supprimer/ }))

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        "Une erreur est survenue lors de la suppression de l'image",
        expect.any(String)
      )
    })
  })
})
