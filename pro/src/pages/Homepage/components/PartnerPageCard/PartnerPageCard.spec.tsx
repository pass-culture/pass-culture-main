import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { forwardRef } from 'react'
import { axe } from 'vitest-axe'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events, HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { imageFileFactory } from '@/commons/utils/factories/imageUploadArgsFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { postImageToVenue } from '@/repository/pcapi/pcapi'

import { HomepageVariant } from '../types'
import { PartnerPageCard } from './PartnerPageCard'

const mockLogEvent = vi.fn()

const IMAGE_INPUT_LABEL = 'Importez ou déposez le fichier ici'

vi.mock('@/commons/utils/config', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/config')),
    WEBAPP_URL: 'https://mon-url-de-base',
  }
})

vi.mock('@/commons/utils/imageUpload/getImageDimensions', () => ({
  getImageDimensions: vi.fn((file) => {
    return Promise.resolve({
      width: (file as any).width || 0,
      height: (file as any).height || 0,
    })
  }),
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

vi.mock('@/commons/utils/prepareImageForUpload', () => ({
  prepareImageForUpload: vi.fn(async (file: File) => file),
}))

vi.mock('@/repository/pcapi/pcapi', () => ({ postImageToVenue: vi.fn() }))

const createImage = () =>
  Object.assign(imageFileFactory('fake_img.jpg'), { width: 100, height: 100 })

const baseVenue = makeGetVenueResponseModel({
  id: 1,
  managingOffererId: 1,
  publicName: 'Club Dorothy',
})

const renderPartnerPageCard = (
  variant: HomepageVariant = HomepageVariant.INDIVIDUAL,
  venueOverrides?: Partial<GetVenueResponseModel>,
  isReadOnly = false
) => {
  const venue = makeGetVenueResponseModel({
    ...baseVenue,
    ...venueOverrides,
  })
  return renderWithProviders(
    <PartnerPageCard
      isReadOnly={isReadOnly}
      venueId={venue.id}
      venueName={venue.publicName}
      venueBannerUrl={venue.bannerUrl}
      venueBannerMeta={venue.bannerMeta}
      variant={variant}
    />
  )
}

describe('PartnerPageCard', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })
  it('should render without accessibility violations', async () => {
    const { container } = renderPartnerPageCard(HomepageVariant.INDIVIDUAL, {
      bannerMeta: {
        image_credit: null,
        original_image_url: 'MyFirstImage',
        crop_params: {
          height_crop_percent: 12,
          width_crop_percent: 12,
          x_crop_percent: 12,
          y_crop_percent: 12,
        },
      },
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the partner page module with the venue information', () => {
    renderPartnerPageCard(HomepageVariant.INDIVIDUAL, {
      bannerMeta: {
        image_credit: null,
        original_image_url: 'MyFirstImage',
        crop_params: {
          height_crop_percent: 12,
          width_crop_percent: 12,
          x_crop_percent: 12,
          y_crop_percent: 12,
        },
      },
    })

    expect(screen.getByText('Club Dorothy')).toBeVisible()
    const image = screen.getByAltText('Prévisualisation de l’image')
    expect(image).toHaveAttribute('src', 'MyFirstImage')
  })

  it('should render image uploader when venue has no image', () => {
    renderPartnerPageCard()

    expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeEnabled()
  })

  it('should log CLICKED_ADD_IMAGE on image upload', async () => {
    const user = userEvent.setup()
    const mockFile = Object.assign(imageFileFactory('fake_img.jpg'), {
      width: 100,
      height: 100,
    })

    renderPartnerPageCard()

    const imageInput = screen.getByLabelText(IMAGE_INPUT_LABEL)
    expect(imageInput).toBeInTheDocument()
    await user.upload(imageInput, mockFile)

    await waitFor(() => {
      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_ADD_IMAGE, {
        imageType: UploaderModeEnum.VENUE,
        isEdition: true,
        imageCreationStage: 'add image',
      })
    })
    expect(
      await screen.findByRole('heading', { name: 'Modifier une image' })
    ).toBeInTheDocument()
  })

  it('should display an error and not open the image edition modal when the file is not an image', async () => {
    const user = userEvent.setup()
    renderPartnerPageCard()
    const imageInput = screen.getByLabelText(IMAGE_INPUT_LABEL)

    await user.upload(
      imageInput,
      new File(['not an image'], 'fake_img.jpg', { type: 'image/jpeg' })
    )

    await waitFor(() => {
      expect(imageInput).toHaveAccessibleDescription(
        expect.stringContaining('Le format de l’image n’est pas valide')
      )
    })
    expect(imageInput).toBeInvalid()
    expect(imageInput).toHaveFocus()
    expect(mockLogEvent).not.toHaveBeenCalled()
    expect(
      screen.queryByRole('heading', { name: 'Modifier une image' })
    ).not.toBeInTheDocument()
  })

  it('should display the image once imported through the image edition modal', async () => {
    const user = userEvent.setup()
    vi.mocked(postImageToVenue).mockResolvedValue(
      makeGetVenueResponseModel({
        ...baseVenue,
        bannerUrl: 'https://example.com/banner.jpg',
      })
    )

    renderPartnerPageCard()

    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), createImage())
    await user.click(await screen.findByRole('button', { name: 'Importer' }))

    expect(postImageToVenue).toHaveBeenCalledWith(
      1,
      expect.any(File),
      '',
      null,
      { x: 0, y: 0, width: 100, height: 100 }
    )
    expect(
      await screen.findByAltText('Prévisualisation de l’image')
    ).toHaveAttribute('src', 'https://example.com/banner.jpg')
    expect(screen.queryByLabelText(IMAGE_INPUT_LABEL)).not.toBeInTheDocument()
  })

  it('should notify an error when the image upload fails', async () => {
    const user = userEvent.setup()
    const snackBarError = vi.fn()
    // Same object on every render: the image edition modal depends on it.
    vi.spyOn(useSnackBar, 'useSnackBar').mockReturnValue({
      success: vi.fn(),
      error: snackBarError,
    })
    vi.mocked(postImageToVenue).mockRejectedValue(new Error('Upload error'))

    renderPartnerPageCard()

    await user.upload(screen.getByLabelText(IMAGE_INPUT_LABEL), createImage())
    await user.click(await screen.findByRole('button', { name: 'Importer' }))

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        "Une erreur est survenue lors de l'importation de votre image",
        expect.any(String)
      )
    })
    expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeInTheDocument()
  })

  describe('analytics event', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
    })

    it('should log CLICKED_PARTNER_PAGE on "Voir ma page" click', async () => {
      const user = userEvent.setup()

      renderPartnerPageCard(HomepageVariant.INDIVIDUAL)

      await user.click(screen.getByRole('link', { name: /Voir ma page/ }))

      expect(mockLogEvent).toHaveBeenCalledWith(
        HomepageEvents.CLICKED_PARTNER_PAGE
      )
    })

    it('should log CLICKED_PARTNER_PAGE only once on multiple clicks', async () => {
      const user = userEvent.setup()

      renderPartnerPageCard(HomepageVariant.INDIVIDUAL)

      const link = screen.getByRole('link', { name: /Voir ma page/ })
      await user.click(link)
      await user.click(link)

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
    })

    it('should log CLICKED_FILL_PARTNER_PAGE on "Compléter ma page" click', async () => {
      const user = userEvent.setup()

      renderPartnerPageCard(HomepageVariant.INDIVIDUAL)

      await user.click(screen.getByRole('link', { name: /Compléter ma page/ }))

      expect(mockLogEvent).toHaveBeenCalledWith(
        HomepageEvents.CLICKED_FILL_PARTNER_PAGE,
        {
          variant: HomepageVariant.INDIVIDUAL,
        }
      )
    })
  })

  describe('individual variant', () => {
    it('should render the correct title for individual variant', () => {
      renderPartnerPageCard(HomepageVariant.INDIVIDUAL)

      expect(screen.getByText("Votre page sur l'application")).toBeVisible()
    })

    it('should render venue edition link', () => {
      renderPartnerPageCard()

      expect(
        screen.getByRole('link', { name: 'Compléter ma page' })
      ).toHaveAttribute('href', `/partenaire/page-partenaire`)
    })

    it('should render venue page preview link', () => {
      renderPartnerPageCard()

      expect(
        screen.getByRole('link', { name: /Voir ma page/ })
      ).toHaveAttribute('href', `https://mon-url-de-base/lieu/1`)
    })
  })

  describe('collective variant', () => {
    it('should render the correct title for collective variant', () => {
      renderPartnerPageCard(HomepageVariant.COLLECTIVE)

      expect(screen.getByText('Votre page sur ADAGE')).toBeVisible()
    })

    it('should render venue edition link', () => {
      renderPartnerPageCard(HomepageVariant.COLLECTIVE)

      expect(
        screen.getByRole('link', { name: 'Compléter ma page' })
      ).toHaveAttribute('href', `/partenaire/page-collective`)
    })

    it('should not render venue page preview link', () => {
      renderPartnerPageCard(HomepageVariant.COLLECTIVE)

      expect(
        screen.queryByRole('link', { name: /Voir ma page/ })
      ).not.toBeInTheDocument()
    })
  })

  describe('when isReadOnly is true', () => {
    it('should disable the page edition and preview links', () => {
      renderPartnerPageCard(HomepageVariant.INDIVIDUAL, undefined, true)

      const editionLink = screen.getByRole('link', {
        name: 'Compléter ma page',
      })
      expect(editionLink).toHaveAttribute('aria-disabled', 'true')
      expect(editionLink).not.toHaveAttribute('href')

      const previewLink = screen.getByRole('link', { name: /Voir ma page/ })
      expect(previewLink).toHaveAttribute('aria-disabled', 'true')
      expect(previewLink).not.toHaveAttribute('href')
    })

    it('should disable the image uploader', () => {
      renderPartnerPageCard(HomepageVariant.INDIVIDUAL, undefined, true)

      expect(screen.getByLabelText(IMAGE_INPUT_LABEL)).toBeDisabled()
    })
  })
})
