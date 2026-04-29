import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { DMSApplicationstatus } from '@/apiClient/v1/models/DMSApplicationstatus'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  defaultDMSApplicationForEACV2,
  defaultGetVenue,
} from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PartnerPage } from '../PartnerPage'

const mockLogEvent = vi.fn()

const renderPartnerPage = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<PartnerPage />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: { ...defaultGetVenue, ...venueOverrides },
      },
    },
  })

describe('PartnerPage', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should display the venue public name and the address', () => {
    renderPartnerPage()

    expect(
      screen.getByRole('heading', { name: 'Nom public de la structure' })
    ).toBeInTheDocument()
    expect(screen.getByTestId('venue-address')).toBeInTheDocument()
  })

  it('should link "Paramètres généraux" to the venue settings page', () => {
    renderPartnerPage({
      id: 42,
      managingOfferer: { ...defaultGetVenue.managingOfferer, id: 7 },
    })

    expect(
      screen.getByRole('link', { name: 'Paramètres généraux' })
    ).toHaveAttribute('href', '/partenaire/page-individuelle/parametres')
  })

  it('should display image upload and log CLICKED_ADD_IMAGE on click when no image', async () => {
    renderPartnerPage({ id: 42, bannerUrl: null })

    await userEvent.click(screen.getByText(/Ajouter une image/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_ADD_IMAGE, {
      venueId: 42,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  })

  it('should display the image when present', () => {
    renderPartnerPage({
      bannerUrl: 'https://www.example.com/image.png',
      bannerMeta: {
        image_credit: null,
        original_image_url: 'https://www.example.com/image.png',
        crop_params: {
          x_crop_percent: 0,
          y_crop_percent: 0,
          width_crop_percent: 0,
          height_crop_percent: 0,
        },
      },
    })

    expect(screen.getByAltText('Prévisualisation de l’image')).toHaveAttribute(
      'src',
      'https://www.example.com/image.png'
    )
  })

  it('should display the "Grand public" section when the venue has a partner page', () => {
    renderPartnerPage({ hasPartnerPage: true })

    expect(screen.getByText('Grand public')).toBeInTheDocument()
  })

  it('should not display the "Grand public" section when the venue does not have a partner page', () => {
    renderPartnerPage({ hasPartnerPage: false })

    expect(screen.queryByText('Grand public')).not.toBeInTheDocument()
  })

  it('should display the EAC section with the "Déposer un dossier ADAGE" link when not referenced yet', () => {
    renderPartnerPage({
      allowedOnAdage: false,
      lastCollectiveDmsApplication: null,
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(screen.getByText('Déposer un dossier ADAGE')).toBeInTheDocument()
  })

  it('should render VenueOfferSteps when the venue has a DMS application in instruction', () => {
    renderPartnerPage({
      lastCollectiveDmsApplication: {
        ...defaultDMSApplicationForEACV2,
        state: DMSApplicationstatus.EN_INSTRUCTION,
      },
    })

    expect(screen.getByText('Démarche en cours :')).toBeInTheDocument()
  })

  it('should not render VenueOfferSteps when the venue has no in-flight DMS application', () => {
    renderPartnerPage({ lastCollectiveDmsApplication: null })

    expect(screen.queryByText('Démarche en cours :')).not.toBeInTheDocument()
  })
})
