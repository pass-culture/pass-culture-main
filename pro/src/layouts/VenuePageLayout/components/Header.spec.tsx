import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { forwardRef } from 'react'

import { apiNew } from '@/apiClient/api'
import * as apiHelpers from '@/apiClient/helpers'
import {
  DisplayableActivity,
  type GetVenueResponseModel,
} from '@/apiClient/v1/new'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { getActivityLabel } from '@/commons/mappings/mappings'
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

vi.mock('@/components/ImageDragAndDrop/getImageDimensions', () => ({
  getImageDimensions: vi.fn((file) =>
    Promise.resolve({
      width: (file as any).width || 0,
      height: (file as any).height || 0,
    })
  ),
}))

vi.mock('react-avatar-editor', () => {
  const MockAvatarEditor = forwardRef((_props, _ref) => (
    <div data-testid="mock-avatar-editor" />
  ))
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
  beforeEach(async () => {
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    mockUseOnVenueImageUpload.mockReturnValue({
      imageValues: {},
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn(),
    })
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementationOnce(() => ({
      ...snackBarsImport,
      success: snackBarSuccess,
      error: snackBarError,
    }))
  })

  it('should display the venue public name and activity label', () => {
    renderHeader('partnerPage', { activity: DisplayableActivity.FESTIVAL })

    expect(screen.getByText('Nom public de la structure 1')).toBeInTheDocument()
    expect(
      screen.getByText(getActivityLabel(DisplayableActivity.FESTIVAL))
    ).toBeInTheDocument()
  })

  it('should not display any activity label when the venue has no activity', () => {
    renderHeader('partnerPage', { activity: null })

    expect(
      screen.queryByText(getActivityLabel(DisplayableActivity.OTHER))
    ).not.toBeInTheDocument()
  })

  it('should display the image uploader when there is no image', () => {
    renderHeader('partnerPage')

    expect(screen.getByLabelText('Importez une image')).toBeInTheDocument()
  })

  it('should log an event on image upload', async () => {
    const user = userEvent.setup()
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementationOnce(() => ({
      logEvent: mockLogEvent,
    }))

    const mockFile = Object.assign(new File(['fake img'], 'fake_img.jpg'), {
      width: 100,
      height: 100,
    })

    renderHeader('partnerPage')

    await user.upload(screen.getByLabelText('Importez une image'), mockFile)

    await waitFor(() => {
      expect(mockLogEvent).toHaveBeenCalledWith(Events.DRAG_OR_SELECTED_IMAGE, {
        imageType: UploaderModeEnum.VENUE,
        isEdition: true,
        imageCreationStage: 'add image',
      })
    })
  })

  it('should display the preview link for a permanent venue on the partner page', () => {
    renderHeader('partnerPage', { isPermanent: true })

    expect(screen.getByText('Visualiser votre page')).toBeInTheDocument()
  })

  it('should not display the preview link for a non-permanent venue', () => {
    renderHeader('partnerPage', { isPermanent: false })

    expect(screen.queryByText('Visualiser votre page')).not.toBeInTheDocument()
  })

  it('should not display the preview link in the collective context', () => {
    renderHeader('collective', { isPermanent: true })

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

  it('should call the delete endpoint and notify success when deleting the image', async () => {
    const user = userEvent.setup()
    vi.spyOn(apiNew, 'deleteVenueBanner').mockResolvedValueOnce()
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

    expect(apiNew.deleteVenueBanner).toHaveBeenCalledWith({
      path: { venue_id: 1 },
    })
    await waitFor(() => {
      expect(snackBarSuccess).toHaveBeenCalledWith(
        'Votre image a bien été supprimée'
      )
    })
  })

  it('should notify an error when image deletion fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(apiNew, 'deleteVenueBanner').mockRejectedValueOnce(
      'Deletion error'
    )
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
        "Une erreur est survenue lors de la suppression de l'image"
      )
    })
  })
})
