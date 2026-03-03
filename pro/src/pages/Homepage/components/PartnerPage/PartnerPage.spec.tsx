import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PartnerPage } from './PartnerPage'

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
  name: 'Club Dorothy',
})

describe('PartnerPage', () => {
  it('should render the partner page module with the venue information', () => {
    const venue = makeGetVenueResponseModel({
      ...baseVenue,
      bannerMeta: {
        original_image_url: 'MyFirstImage',
        crop_params: {
          height_crop_percent: 12,
          width_crop_percent: 12,
          x_crop_percent: 12,
          y_crop_percent: 12,
        },
      },
    })

    renderWithProviders(<PartnerPage venue={venue} />)

    expect(screen.getByText("Votre page sur l'application")).toBeVisible()
    expect(screen.getByText('Club Dorothy')).toBeVisible()
    const image = screen.getByAltText('Prévisualisation de l’image')
    expect(image).toHaveAttribute('src', 'MyFirstImage')
  })

  it('should render image uploader when venue has no image', () => {
    renderWithProviders(<PartnerPage venue={baseVenue} />)

    expect(screen.getByText('Importez une image')).toBeVisible()
  })

  it('should render venue edition link', () => {
    renderWithProviders(<PartnerPage venue={baseVenue} />)

    expect(
      screen.getByRole('link', { name: 'Compléter ma page' })
    ).toHaveAttribute(
      'href',
      `/structures/${baseVenue.managingOffererId}/lieux/${baseVenue.id}/page-partenaire`
    )
  })

  it('should render venue page preview link', () => {
    renderWithProviders(<PartnerPage venue={baseVenue} />)

    expect(screen.getByRole('link', { name: /Voir ma page/ })).toHaveAttribute(
      'href',
      `https://mon-url-de-base/lieu/${baseVenue.id}`
    )
  })

  it('should log CLICKED_ADD_IMAGE on image upload', async () => {
    const mockFile = Object.assign(new File(['fake img'], 'fake_img.jpg'), {
      width: 100,
      height: 100,
    })

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderWithProviders(<PartnerPage venue={baseVenue} />)

    const imageInput = screen.getByLabelText('Importez une image')
    expect(imageInput).toBeInTheDocument()
    await userEvent.upload(imageInput, mockFile)

    await waitFor(() => {
      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_ADD_IMAGE, {
        offererId: '1',
        venueId: defaultGetVenue.id,
        imageType: UploaderModeEnum.VENUE,
        isEdition: true,
        imageCreationStage: 'add image',
      })
    })
  })
})
