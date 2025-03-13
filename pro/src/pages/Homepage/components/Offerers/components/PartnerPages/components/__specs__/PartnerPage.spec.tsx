import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { VenueTypeCode } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { PartnerPage, PartnerPageProps } from '../PartnerPage'

const mockLogEvent = vi.fn()

const renderPartnerPages = (props: Partial<PartnerPageProps>, features?: string[]) => {
  renderWithProviders(
    <PartnerPage
      offerer={{ ...defaultGetOffererResponseModel }}
      venue={{ ...defaultGetOffererVenueResponseModel }}
      venueTypes={[{ id: VenueTypeCode.FESTIVAL, label: 'Festival' }]}
      {...props}
    />,
    {
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
      features, 
    }
  )
}

describe('PartnerPages', () => {
  it('should display image upload if no image', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
        venueTypeCode: VenueTypeCode.FESTIVAL,
      },
    })

    expect(screen.getByText(/Ajouter une image/)).toBeInTheDocument()
    await userEvent.click(screen.getByText(/Ajouter une image/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_ADD_IMAGE, {
      offererId: '1',
      venueId: defaultGetOffererVenueResponseModel.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  })

  it('should display the image if its present', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
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

  it('should display a "Grand public" section', () => {
    renderPartnerPages({})

    expect(screen.getByText('Grand public')).toBeInTheDocument()
  })

  it('should display the EAC section', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
        collectiveDmsApplications: [],
      },
      offerer: {
        ...defaultGetOffererResponseModel,
        allowedOnAdage: false,
      },
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.getByText('Faire une demande de référencement ADAGE')
    ).toBeInTheDocument()
  })

  describe('when open to public feature is enabled', () => {
    it('should display the "Grand public" section when the venue has a partner page', () => {
      renderPartnerPages({
        venue: {
          ...defaultGetOffererVenueResponseModel,
          hasPartnerPage: true,
        },
      }, ['WIP_IS_OPEN_TO_PUBLIC'])

      expect(screen.getByText('Grand public')).toBeInTheDocument()
    })

    it('should not display the "Grand public" section when the venue does not have a partner page', () => {
      renderPartnerPages({
        venue: {
          ...defaultGetOffererVenueResponseModel,
          hasPartnerPage: false,
        },
      }, ['WIP_IS_OPEN_TO_PUBLIC'])

      expect(screen.queryByText('Grand public')).not.toBeInTheDocument()
    })
  })
})
