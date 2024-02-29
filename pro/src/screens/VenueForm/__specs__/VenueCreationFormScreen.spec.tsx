import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { apiAdresse } from 'apiClient/adresse'
import { api } from 'apiClient/api'
import {
  ApiError,
  SharedCurrentUserResponseModel,
  VenueTypeCode,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { VenueFormValues } from 'components/VenueCreationForm'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueCreationFormScreen } from '../VenueCreationFormScreen'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const venueTypes: SelectOption[] = [
  { value: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { value: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const venueLabels: SelectOption[] = [
  { value: 'AE', label: 'Architecture contemporaine remarquable' },
  {
    value: 'A9',
    label: "CAC - Centre d'art contemporain d’int\u00e9r\u00eat national",
  },
]

const renderForm = (
  currentUser: SharedCurrentUserResponseModel,
  initialValues: VenueFormValues
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser,
    },
  }

  renderWithProviders(
    <>
      <Routes>
        <Route
          path="/structures/AE/lieux/creation"
          element={
            <>
              <VenueCreationFormScreen
                initialValues={initialValues}
                offerer={{
                  ...defaultGetOffererResponseModel,
                  id: 12,
                  siren: '881457238',
                }}
                venueTypes={venueTypes}
                venueLabels={venueLabels}
                providers={[]}
                venueProviders={[]}
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
    { storeOverrides, initialRouterEntries: ['/structures/AE/lieux/creation'] }
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

describe('VenueFormScreen', () => {
  let formValues: VenueFormValues

  beforeEach(() => {
    formValues = {
      bannerMeta: undefined,
      comment: '',
      description: '',
      isVenueVirtual: false,
      bookingEmail: 'em@ail.fr',
      name: 'MINISTERE DE LA CULTURE',
      publicName: 'Melodie Sims',
      siret: '88145723823022',
      venueType: VenueTypeCode.JEUX_JEUX_VID_OS,
      venueLabel: 'EM',
      departmentCode: '',
      address: 'PARIS',
      banId: '35288_7283_00001',
      addressAutocomplete: 'Allee Rene Omnes 35400 Saint-Malo',
      'search-addressAutocomplete': 'PARIS',
      city: 'Saint-Malo',
      latitude: 48.635699,
      longitude: -2.006961,
      postalCode: '35400',
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
      isPermanent: false,
      id: undefined,
      bannerUrl: '',
      withdrawalDetails: 'withdrawal details field',
      venueSiret: null,
      isWithdrawalAppliedOnAllOffers: false,
      reimbursementPointId: 91,
    }
    vi.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue({
      canCreate: true,
    })
  })

  it('should redirect user with the new creation journey', async () => {
    vi.spyOn(api, 'postCreateVenue').mockResolvedValue({ id: 56 })
    renderForm(
      {
        id: 12,
        isAdmin: true,
      } as SharedCurrentUserResponseModel,
      formValues
    )

    await userEvent.click(screen.getByText(/Enregistrer et créer le lieu/))
    await waitFor(() => {
      expect(screen.getByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    })
  })

  it('should redirect user with the creation popin displayed', async () => {
    renderForm(
      {
        id: 12,
        isAdmin: false,
      } as SharedCurrentUserResponseModel,
      formValues
    )
    vi.spyOn(api, 'postCreateVenue').mockResolvedValue({ id: 56 })

    await userEvent.click(screen.getByText(/Enregistrer et créer le lieu/))

    await waitFor(() => {
      expect(screen.queryByText(PATCH_SUCCESS_MESSAGE)).not.toBeInTheDocument()
    })
  })

  it('should redirect user to the edit page after creating a venue', async () => {
    renderForm(
      {
        id: 12,
        isAdmin: true,
      } as SharedCurrentUserResponseModel,
      formValues
    )
    vi.spyOn(api, 'postCreateVenue').mockResolvedValue({ id: 56 })

    await userEvent.click(screen.getByText(/Enregistrer et créer le lieu/))

    await waitFor(() => {
      expect(screen.getByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    })
  })

  it('should display an error when the venue could not be created', async () => {
    renderForm(
      {
        id: 12,
        isAdmin: true,
      } as SharedCurrentUserResponseModel,
      formValues
    )

    vi.spyOn(api, 'postCreateVenue').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            siret: ['ensure this value has at least 14 characters'],
          },
        } as ApiResult,
        ''
      )
    )

    await userEvent.click(screen.getByText(/Enregistrer/))

    await waitFor(() => {
      expect(
        screen.getByText('ensure this value has at least 14 characters')
      ).toBeInTheDocument()
    })
  })

  it('Submit creation form that fails with unknown error', async () => {
    renderForm(
      {
        id: 12,
        isAdmin: true,
      } as SharedCurrentUserResponseModel,
      formValues
    )

    const postCreateVenue = vi
      .spyOn(api, 'postCreateVenue')
      .mockRejectedValue({})

    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(postCreateVenue).toHaveBeenCalled()
    await waitFor(() => {
      expect(
        screen.getByText('Erreur inconnue lors de la sauvegarde du lieu.')
      ).toBeInTheDocument()
    })
  })

  describe('Displaying with new onboarding', () => {
    it('should render errors on creation', async () => {
      formValues.venueType = ''
      formValues.name = ''
      formValues.publicName = ''
      renderForm(
        {
          id: 12,
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues
      )

      await userEvent.click(screen.getByText(/Enregistrer et créer le lieu/))

      expect(
        await screen.findByText(
          'Veuillez renseigner la raison sociale de votre lieu'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText('Veuillez sélectionner une activité principale')
      ).toBeInTheDocument()
    })
  })

  it('should display eac section during venue creation if venue has siret and is eligible to eac', async () => {
    renderForm(
      {
        id: 12,
        isAdmin: false,
      } as SharedCurrentUserResponseModel,
      formValues
    )
    await waitFor(
      () => expect(api.canOffererCreateEducationalOffer).toHaveBeenCalled
    )
    expect(
      screen.queryByRole('heading', {
        name: 'Mes informations pour les enseignants',
      })
    ).toBeInTheDocument()
  })
})
