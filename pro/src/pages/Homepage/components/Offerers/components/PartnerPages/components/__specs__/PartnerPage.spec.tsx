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

const renderPartnerPages = (props: Partial<PartnerPageProps>) => {
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
})
