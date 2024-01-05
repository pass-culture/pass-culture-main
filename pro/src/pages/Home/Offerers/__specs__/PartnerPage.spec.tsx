import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import * as router from 'react-router-dom'

import { DMSApplicationstatus, VenueTypeCode } from 'apiClient/v1'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { defaultGetOffererVenueResponseModel } from 'utils/apiFactories'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PartnerPage, PartnerPageProps } from '../PartnerPage'

const mockLogEvent = vi.fn()

const renderPartnerPages = (props: PartnerPageProps) => {
  renderWithProviders(<PartnerPage {...props} />)
}

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLoaderData: vi.fn(),
}))

describe('PartnerPages', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useLoaderData').mockReturnValue({
      venueTypes: [{ id: VenueTypeCode.FESTIVAL, label: 'Festival' }],
    })
  })

  it('should display image upload if no image', async () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
        venueTypeCode: VenueTypeCode.FESTIVAL,
      },
      offererId: '1',
    })

    expect(screen.getByText(/Ajouter une image/)).toBeInTheDocument()
    await userEvent.click(screen.getByText(/Ajouter une image/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_ADD_IMAGE, {
      venueId: defaultGetOffererVenueResponseModel.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
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
      offererId: '1',
    })

    expect(screen.getByAltText('Prévisualisation de l’image')).toHaveAttribute(
      'src',
      'https://www.example.com/image.png'
    )
  })

  it('should display the EAC section when no adage', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
        collectiveDmsApplications: [],
      },
      offererId: '1',
    })

    expect(screen.getByText('Non référencé sur ADAGE')).toBeInTheDocument()
  })

  it('should display the EAC section when adage refused', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
        collectiveDmsApplications: [
          {
            ...defaultCollectiveDmsApplication,
            state: DMSApplicationstatus.REFUSE,
          },
        ],
      },
      offererId: '1',
    })

    expect(screen.getByText('Non référencé sur ADAGE')).toBeInTheDocument()
  })

  it('should display the EAC section when adage application in progress', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
        collectiveDmsApplications: [
          {
            ...defaultCollectiveDmsApplication,
            state: DMSApplicationstatus.EN_INSTRUCTION,
          },
        ],
      },
      offererId: '1',
    })

    expect(screen.getByText('Référencement en cours')).toBeInTheDocument()
  })

  it('should display the EAC section when adage application accepted', () => {
    renderPartnerPages({
      venue: {
        ...defaultGetOffererVenueResponseModel,
        collectiveDmsApplications: [
          {
            ...defaultCollectiveDmsApplication,
            state: DMSApplicationstatus.ACCEPTE,
          },
        ],
      },
      offererId: '1',
    })

    expect(screen.getByText('Référencé sur ADAGE')).toBeInTheDocument()
  })
})
