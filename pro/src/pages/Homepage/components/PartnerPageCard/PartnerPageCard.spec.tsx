import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events, HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { HomepageVariant } from '../types'
import { PartnerPageCard } from './PartnerPageCard'

const mockLogEvent = vi.fn()

vi.mock('@/commons/utils/config', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/config')),
    WEBAPP_URL: 'https://mon-url-de-base',
  }
})

vi.mock('@/components/ImageDragAndDrop/getImageDimensions', () => ({
  getImageDimensions: vi.fn((file) => {
    return Promise.resolve({
      width: (file as any).width || 0,
      height: (file as any).height || 0,
    })
  }),
}))

const baseVenue = makeGetVenueResponseModel({
  id: 1,
  managingOffererId: 1,
  publicName: 'Club Dorothy',
})

const renderPartnerPageCard = (
  variant: HomepageVariant = HomepageVariant.INDIVIDUAL,
  venueOverrides?: Partial<GetVenueResponseModel>
) => {
  const venue = makeGetVenueResponseModel({
    ...baseVenue,
    ...venueOverrides,
  })
  return renderWithProviders(
    <PartnerPageCard
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

    expect(screen.getByText('Importez une image')).toBeVisible()
  })

  it('should log CLICKED_ADD_IMAGE on image upload', async () => {
    const user = userEvent.setup()
    const mockFile = Object.assign(new File(['fake img'], 'fake_img.jpg'), {
      width: 100,
      height: 100,
    })

    renderPartnerPageCard()

    const imageInput = screen.getByLabelText('Importez une image')
    expect(imageInput).toBeInTheDocument()
    await user.upload(imageInput, mockFile)

    await waitFor(() => {
      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_ADD_IMAGE, {
        imageType: UploaderModeEnum.VENUE,
        isEdition: true,
        imageCreationStage: 'add image',
      })
    })
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
})
