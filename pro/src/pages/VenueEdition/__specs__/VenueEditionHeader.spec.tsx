import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { VenueTypeCode } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Events } from 'core/FirebaseEvents/constants'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

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
      {...props}
    />,
    { ...options }
  )
}

describe('PartnerPages', () => {
  it('should display image upload if no image', async () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderPartnerPages({
      venue: {
        ...defaultGetVenue,
        venueTypeCode: VenueTypeCode.FESTIVAL,
      },
    })

    expect(screen.getByText(/Ajouter une image/)).toBeInTheDocument()
    await userEvent.click(screen.getByText(/Ajouter une image/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_ADD_IMAGE, {
      venueId: defaultGetVenue.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
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

  it('should not display new offer button in new nav', () => {
    renderPartnerPages(
      {
        venue: {
          ...defaultGetVenue,
          venueTypeCode: VenueTypeCode.FESTIVAL,
        },
      },
      {
        user: sharedCurrentUserFactory({
          navState: { newNavDate: '2002-07-29T12:18:43.087097Z' },
        }),
      }
    )

    expect(screen.queryByText('Créer une offre')).not.toBeInTheDocument()
  })
})
