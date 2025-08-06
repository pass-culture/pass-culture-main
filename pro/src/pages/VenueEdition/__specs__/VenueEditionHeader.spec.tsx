import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { VenueTypeCode } from '@/apiClient//v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  VenueEditionHeader,
  VenueEditionHeaderProps,
} from '../VenueEditionHeader'

const mockLogEvent = vi.fn()

const renderPartnerPages = (
  props: Partial<VenueEditionHeaderProps>,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <VenueEditionHeader
      offerer={{ ...defaultGetOffererResponseModel }}
      venue={{ ...defaultGetVenue }}
      venueTypes={[{ id: VenueTypeCode.FESTIVAL, label: 'Festival' }]}
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

describe('VenueEditionHeader', () => {
  it('should display image upload if no image', async () => {
    const mockFile = new File(['fake img'], 'fake_img.jpg', {
      type: 'image/jpeg',
    })

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        venueTypeCode: VenueTypeCode.FESTIVAL,
      },
    })

    const imageInput = screen.getByLabelText('Importez une image')
    expect(imageInput).toBeInTheDocument()
    await userEvent.upload(imageInput, mockFile)

    expect(mockLogEvent).toHaveBeenCalledWith(Events.DRAG_OR_SELECTED_IMAGE, {
      offererId: '1',
      venueId: defaultGetVenue.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  })

  it('should display the image if its present', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        venueTypeCode: VenueTypeCode.FESTIVAL,
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
        venueTypeCode: VenueTypeCode.FESTIVAL,
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
          venueTypeCode: VenueTypeCode.FESTIVAL,
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
})
