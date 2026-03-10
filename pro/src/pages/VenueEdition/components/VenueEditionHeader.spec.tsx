import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { forwardRef } from 'react'

import { api } from '@/apiClient/api'
import * as apiHelpers from '@/apiClient/helpers'
import { VenueTypeCode } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  VenueEditionHeader,
  type VenueEditionHeaderProps,
} from './VenueEditionHeader'

const mockLogEvent = vi.fn()

vi.mock('@/components/ImageDragAndDrop/getImageDimensions', () => ({
  getImageDimensions: vi.fn((file) => {
    return Promise.resolve({
      width: (file as any).width || 0,
      height: (file as any).height || 0,
    })
  }),
}))

vi.mock('react-avatar-editor', () => {
  const MockAvatarEditor = forwardRef((_props, _ref) => {
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
  useSWRConfig: vi.fn(() => ({
    mutate: mockMutate,
  })),
}))

const mockUseOnVenueImageUpload = vi.hoisted(() => vi.fn())
vi.mock('@/commons/core/Venue/hooks/useOnVenueImageUpload', () => ({
  useOnVenueImageUpload: mockUseOnVenueImageUpload,
}))

const renderPartnerPages = (
  props: Partial<VenueEditionHeaderProps>,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <VenueEditionHeader
      venue={{ ...defaultGetVenue }}
      context="partnerPage"
      {...props}
    />,
    {
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
      ...options,
    }
  )
}
const snackBarSuccess = vi.fn()
const snackBarError = vi.fn()

describe('VenueEditionHeader', () => {
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

  it('should display image upload if no image', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        venueType: { value: VenueTypeCode.FESTIVAL, label: 'Festival' },
      },
    })

    const imageInput = screen.getByLabelText('Importez une image')
    expect(imageInput).toBeInTheDocument()
  })

  it('should log event on image upload', async () => {
    const mockFile = Object.assign(new File(['fake img'], 'fake_img.jpg'), {
      width: 100,
      height: 100,
    })

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementationOnce(() => ({
      logEvent: mockLogEvent,
    }))

    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        venueType: { value: VenueTypeCode.FESTIVAL, label: 'Festival' },
      },
    })

    const imageInput = screen.getByLabelText('Importez une image')
    await userEvent.upload(imageInput, mockFile)

    await waitFor(() => {
      expect(mockLogEvent).toHaveBeenCalledWith(Events.DRAG_OR_SELECTED_IMAGE, {
        offererId: '1',
        venueId: defaultGetVenue.id,
        imageType: UploaderModeEnum.VENUE,
        isEdition: true,
        imageCreationStage: 'add image',
      })
    })
  })

  it('should display the image if its present', () => {
    mockUseOnVenueImageUpload.mockReturnValueOnce({
      imageValues: {
        croppedImageUrl: 'https://www.example.com/image.png',
        credit: '',
      },
      setImageValues: vi.fn(),
      handleOnImageUpload: vi.fn(),
    })
    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        venueType: { value: VenueTypeCode.FESTIVAL, label: 'Festival' },
        bannerUrl: 'https://www.example.com/image.png',
        bannerMeta: {
          original_image_url: 'https://www.example.com/image.png',
          image_credit: '',
          crop_params: {
            x_crop_percent: 0,
            y_crop_percent: 0,
            width_crop_percent: 0,
            height_crop_percent: 0,
          },
        },
      },
    })

    expect(screen.getByAltText('Prévisualisation de l’image')).toHaveAttribute(
      'src',
      'https://www.example.com/image.png'
    )
  })

  it('should display a preview link when venue is permanent', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        venueType: { value: VenueTypeCode.FESTIVAL, label: '' },
        isPermanent: true,
      },
    })

    expect(screen.getByText('Visualiser votre page')).toBeInTheDocument()
  })

  it('should not display new offer button in new nav', () => {
    renderPartnerPages(
      {
        venue: {
          ...defaultGetVenue,
          venueType: { value: VenueTypeCode.FESTIVAL, label: '' },
        },
      },
      {
        user: sharedCurrentUserFactory(),
        storeOverrides: {
          user: { currentUser: sharedCurrentUserFactory() },
          offerer: currentOffererFactory(),
        },
      }
    )

    expect(screen.queryByText('Créer une offre')).not.toBeInTheDocument()
  })

  it('should not display "Visualiser votre page" for adage venues', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
      },
      context: 'collective',
    })

    expect(screen.queryByText('Visualiser votre page')).not.toBeInTheDocument()
  })

  it('should display a "Paramètres généraux" link', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
      },
    })

    const link = screen.getByRole('link', {
      name: 'Paramètres généraux',
    })

    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute(
      'href',
      `/structures/${defaultGetOffererResponseModel.id}/lieux/${defaultGetVenue.id}/parametres`
    )
  })

  it('should call delete endpoint and mutate venue when deleting image', async () => {
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

    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        bannerUrl: 'https://www.example.com/image.png',
        bannerMeta: {
          original_image_url: 'https://www.example.com/image.png',
          image_credit: '',
          crop_params: {
            x_crop_percent: 0,
            y_crop_percent: 0,
            width_crop_percent: 0,
            height_crop_percent: 0,
          },
        },
      },
    })

    const updateImageButton = screen.getByRole('button', {
      name: 'Modifier l’image',
    })
    userEvent.click(updateImageButton)

    const deleteButton = await screen.findByRole('button', {
      name: 'Supprimer l’image',
    })
    userEvent.click(deleteButton)

    await waitFor(() => {
      expect(api.deleteVenueBanner).toHaveBeenCalledWith(defaultGetVenue.id)
      expect(mockMutate).toHaveBeenCalledWith(
        [GET_VENUE_QUERY_KEY, String(defaultGetVenue.id)],
        expect.any(Function)
      )
      expect(snackBarSuccess).toHaveBeenCalledWith(
        'Votre image a bien été supprimée'
      )
    })
  })

  it('should show snackbar error when image deletion fails', async () => {
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

    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        bannerUrl: 'https://www.example.com/image.png',
        bannerMeta: {
          original_image_url: 'https://www.example.com/image.png',
          image_credit: '',
          crop_params: {
            x_crop_percent: 0,
            y_crop_percent: 0,
            width_crop_percent: 0,
            height_crop_percent: 0,
          },
        },
      },
    })

    const updateImageButton = screen.getByRole('button', {
      name: 'Modifier l’image',
    })
    userEvent.click(updateImageButton)

    const deleteButton = await screen.findByRole('button', {
      name: 'Supprimer l’image',
    })
    userEvent.click(deleteButton)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        "Une erreur est survenue lors de la suppression de l'image"
      )
    })
  })
})
