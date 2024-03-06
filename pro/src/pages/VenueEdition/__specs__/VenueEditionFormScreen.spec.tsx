import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { apiAdresse } from 'apiClient/adresse'
import { api } from 'apiClient/api'
import { ApiError, GetVenueResponseModel, VenueTypeCode } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueEditionFormValues } from '../types'
import { VenueEditionFormScreen } from '../VenueEditionFormScreen'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const renderForm = (
  initialValues: VenueEditionFormValues,
  venue: GetVenueResponseModel,
  isAdmin = false,
  hasBookingQuantity?: boolean,
  features: string[] = []
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        id: 'user_id',
        isAdmin,
      },
    },
  }

  renderWithProviders(
    <>
      <Routes>
        <Route
          path="/structures/AE/lieux/creation"
          element={
            <>
              <VenueEditionFormScreen
                initialValues={initialValues}
                venue={venue}
              />
            </>
          }
        />
        <Route
          path="/structures/AE/lieux/:venueId"
          element={
            <>
              <div>Lieu créé</div>
            </>
          }
        />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: ['/structures/AE/lieux/creation'],
      features,
    }
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: vi.fn(),
    getSiretInfo: vi.fn(),
    editVenue: vi.fn(),
    getEducationalPartners: vi.fn(() => Promise.resolve({ partners: [] })),
    getAvailableReimbursementPoints: vi.fn(() => Promise.resolve([])),
    canOffererCreateEducationalOffer: vi.fn(),
  },
}))
vi.spyOn(api, 'getSiretInfo').mockResolvedValue({
  active: true,
  address: {
    city: 'paris',
    postalCode: '75008',
    street: 'rue de paris',
  },
  name: 'lieu',
  siret: '88145723823022',
  ape_code: '95.07A',
  legal_category_code: '1000',
})

vi.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue({
  canCreate: true,
})

vi.mock('apiClient/adresse', async () => {
  return {
    ...((await vi.importActual('apiClient/adresse')) ?? {}),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
  },
])

// Mock l’appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
fetchMock.mockResponse(
  JSON.stringify({
    features: [
      {
        properties: {
          name: 'name',
          city: 'city',
          id: 'id',
          label: 'label',
          postcode: 'postcode',
        },
        geometry: {
          coordinates: [0, 0],
        },
      },
    ],
  }),
  { status: 200 }
)

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('core/Venue/siretApiValidate', () => ({
  default: () => Promise.resolve(),
}))

const venueResponse: GetVenueResponseModel = {
  hasPendingBankInformationApplication: false,
  demarchesSimplifieesApplicationId: '',
  collectiveDomains: [],
  dateCreated: '2022-02-02',
  isVirtual: false,
  visualDisabilityCompliant: false,
  audioDisabilityCompliant: false,
  motorDisabilityCompliant: false,
  mentalDisabilityCompliant: false,
  address: 'Address',
  bannerMeta: null,
  bannerUrl: '',
  city: 'city',
  comment: 'comment',
  contact: {
    email: 'email',
    phoneNumber: '0606060606',
    website: 'web',
  },
  description: 'description',
  departementCode: '75008',
  dmsToken: 'dms-token-12345',
  isPermanent: true,
  latitude: 0,
  longitude: 0,
  bookingEmail: 'a@b.c',
  name: 'name',
  id: 0,
  pricingPoint: null,
  postalCode: '75008',
  publicName: 'name',
  siret: '88145723823022',
  timezone: 'Europe/Paris',
  venueTypeCode: VenueTypeCode.COURS_ET_PRATIQUE_ARTISTIQUES,
  venueLabelId: 1,
  reimbursementPointId: 0,
  withdrawalDetails: 'string',
  collectiveAccessInformation: 'string',
  collectiveDescription: 'string',
  collectiveEmail: 'string',
  collectiveInterventionArea: [],
  collectiveLegalStatus: null,
  collectiveNetwork: [],
  collectivePhone: 'string',
  collectiveStudents: [],
  collectiveWebsite: 'string',
  adageInscriptionDate: null,
  hasAdageId: false,
  collectiveDmsApplications: [],
  managingOfferer: {
    address: null,
    city: 'string',
    dateCreated: 'string',
    demarchesSimplifieesApplicationId: null,
    id: 1,
    isValidated: true,
    name: 'name',
    postalCode: 'string',
    siren: null,
  },
}

describe('VenueFormScreen', () => {
  let formValues: VenueEditionFormValues
  let venue: GetVenueResponseModel

  beforeEach(() => {
    formValues = {
      description: '',
      accessibility: {
        visual: false,
        mental: true,
        audio: false,
        motor: true,
        none: false,
      },
      isAccessibilityAppliedOnAllOffers: false,
      phoneNumber: '0604855967',
      email: 'em@ail.com',
      webSite: 'https://www.site.web',
    }

    venue = {
      ...defaultGetVenue,
      hasPendingBankInformationApplication: false,
      demarchesSimplifieesApplicationId: '',
      collectiveDomains: [],
      dateCreated: '2022-02-02',
      isVirtual: false,
      address: 'Address',
      banId: 'ban_id',
      bannerMeta: null,
      bannerUrl: '',
      city: 'city',
      comment: 'comment',
      contact: {
        email: 'email',
        phoneNumber: '0606060606',
        website: 'web',
      },
      description: 'description',
      departementCode: '75008',
      dmsToken: '',
      isPermanent: true,
      latitude: 0,
      longitude: 0,
      name: 'name',
      id: 15,
      pricingPoint: null,
      postalCode: '75008',
      publicName: 'name',
      siret: '88145723823022',
      reimbursementPointId: 0,
      withdrawalDetails: 'string',
      collectiveAccessInformation: 'string',
      collectiveDescription: 'string',
      collectiveEmail: 'string',
      collectiveInterventionArea: [],
      collectiveLegalStatus: null,
      collectiveNetwork: [],
      collectivePhone: 'string',
      collectiveStudents: [],
      collectiveWebsite: 'string',
      managingOfferer: {
        address: null,
        city: 'string',
        dateCreated: 'string',
        demarchesSimplifieesApplicationId: null,
        id: 1,
        isValidated: true,
        name: 'name',
        postalCode: 'string',
        siren: null,
      },
      hasAdageId: false,
      adageInscriptionDate: null,
      bankAccount: null,
    }
  })

  it('should display the partner info', async () => {
    renderForm(formValues, venue, false)

    expect(
      await screen.findByText(
        'Les informations que vous renseignez ci-dessous sont affichées dans votre page partenaire, visible sur l’application pass Culture'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText('État de votre page partenaire sur l’application :')
    ).toBeInTheDocument()
    expect(screen.getByText('Non visible')).toBeInTheDocument()
  })

  it('should display an error when the venue could not be updated', async () => {
    renderForm(formValues, venue)

    vi.spyOn(api, 'editVenue').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            email: ['ensure this is an email'],
          },
        } as ApiResult,
        ''
      )
    )

    await userEvent.click(screen.getByText(/Enregistrer/))

    await waitFor(() => {
      expect(screen.getByText('ensure this is an email')).toBeInTheDocument()
    })
  })

  it('should display specific message when venue is virtual', () => {
    venue.isVirtual = true
    renderForm(formValues, venue)

    expect(
      screen.getByText(
        /Ce lieu vous permet uniquement de créer des offres numériques/
      )
    ).toBeInTheDocument()

    expect(screen.queryAllByRole('input')).toHaveLength(0)
  })

  it('should let update venue without siret', async () => {
    const testedVenue = {
      ...venue,
      siret: null,
    }

    renderForm(formValues, testedVenue)

    const editVenue = vi
      .spyOn(api, 'editVenue')
      .mockResolvedValue(venueResponse)

    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(editVenue).toHaveBeenCalled()
    expect(editVenue).not.toHaveBeenCalledWith(15, { siret: '' })
  })

  it('should diplay only some fields when the venue is virtual', async () => {
    venue.isVirtual = true

    renderForm(formValues, venue, false)

    await waitFor(() => {
      expect(screen.queryByTestId('wrapper-publicName')).not.toBeInTheDocument()
    })

    expect(screen.queryByTestId('wrapper-description')).not.toBeInTheDocument()
    expect(screen.queryByTestId('wrapper-venueLabel')).not.toBeInTheDocument()
    expect(screen.queryByText('Accessibilité du lieu')).not.toBeInTheDocument()
    expect(
      screen.queryByText('Informations de retrait de vos offres')
    ).not.toBeInTheDocument()
    expect(screen.queryByText('Contact')).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).not.toBeInTheDocument()
  })
})
