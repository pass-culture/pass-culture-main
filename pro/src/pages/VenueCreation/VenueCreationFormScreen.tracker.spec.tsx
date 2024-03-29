import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import * as useAnalytics from 'hooks/useAnalytics'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueCreationFormValues } from './types'
import { VenueCreationFormScreen } from './VenueCreationFormScreen'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const venueTypes: SelectOption[] = [
  { value: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { value: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const formValues: VenueCreationFormValues = {
  bannerMeta: undefined,
  comment: '',
  bookingEmail: 'em@ail.fr',
  name: 'MINISTERE DE LA CULTURE',
  publicName: 'Melodie Sims',
  siret: '88145723823022',
  venueType: 'GAMES',
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
  bannerUrl: '',
}

const renderForm = () => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
      },
    },
  }

  renderWithProviders(
    <Routes>
      <Route
        path="/structures/AE/lieux/creation"
        element={
          <VenueCreationFormScreen
            initialValues={formValues}
            offerer={{
              ...defaultGetOffererResponseModel,
              id: 12,
              siren: '881457238',
            }}
            venueTypes={venueTypes}
          />
        }
      />
      <Route
        path="/structures/AE/lieux/:venueId"
        element={<div>Lieu créé</div>}
      />
    </Routes>,
    { storeOverrides, initialRouterEntries: ['/structures/AE/lieux/creation'] }
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: vi.fn(),
    getSiretInfo: vi.fn(),
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

vi.mock('core/Venue/siretApiValidate', () => ({
  default: () => Promise.resolve(),
}))

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

const mockLogEvent = vi.fn()

describe('venue form trackers', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should track success of form submit', async () => {
    renderForm()
    vi.spyOn(api, 'postCreateVenue').mockResolvedValue({
      id: 1,
    })

    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      from: `/structures/AE/lieux/creation`,
      saved: true,
      isEdition: false,
    })
  })

  it('should track failing of form submit', async () => {
    renderForm()
    vi.spyOn(api, 'postCreateVenue').mockRejectedValue({})

    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      from: `/structures/AE/lieux/creation`,
      saved: false,
      isEdition: false,
    })
  })
})
