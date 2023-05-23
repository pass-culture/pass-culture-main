import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetch from 'jest-fetch-mock'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { IVenueFormValues } from 'components/VenueForm'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { IOfferer } from 'core/Offerers/types'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueFormScreen } from '../index'

const venueTypes: SelectOption[] = [
  { value: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { value: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const venueLabels: SelectOption[] = [
  { value: 'AE', label: 'Architecture contemporaine remarquable' },
  {
    value: 'A9',
    label: "CAC - Centre d'art contemporain d'int\u00e9r\u00eat national",
  },
]

const formValues: IVenueFormValues = {
  bannerMeta: undefined,
  comment: '',
  description: '',
  isVenueVirtual: false,
  bookingEmail: 'em@ail.fr',
  name: 'MINISTERE DE LA CULTURE',
  publicName: 'Melodie Sims',
  siret: '88145723823022',
  venueType: 'GAMES',
  venueLabel: 'BM',
  departmentCode: '',
  address: 'PARIS',
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
  withdrawalDetails: 'Oui',
  venueSiret: null,
  isWithdrawalAppliedOnAllOffers: false,
  reimbursementPointId: 91,
}

const renderForm = (isCreation: boolean) => {
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
          <VenueFormScreen
            initialValues={formValues}
            isCreatingVenue={isCreation}
            offerer={{ id: 'AE', siren: '881457238' } as IOfferer}
            venueTypes={venueTypes}
            venueLabels={venueLabels}
            providers={[]}
            venueProviders={[]}
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

jest.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: jest.fn(),
    getSiretInfo: jest.fn(),
  },
}))

jest.spyOn(api, 'getSiretInfo').mockResolvedValue({
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

// Mock l'appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
fetch.mockResponse(
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

const mockLogEvent = jest.fn()

describe('venue form trackers', () => {
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('Tracking success form submit', async () => {
    renderForm(true)
    jest.spyOn(api, 'postCreateVenue').mockResolvedValue({
      id: 'ID',
    } as GetVenueResponseModel)

    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      from: `/structures/AE/lieux/creation`,
      saved: true,
    })
  })

  it('Tracking failing form submit', async () => {
    renderForm(true)
    jest.spyOn(api, 'postCreateVenue').mockRejectedValue({})

    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      from: `/structures/AE/lieux/creation`,
      saved: false,
    })
  })

  it('Tracking offer creation submit', async () => {
    renderForm(false)

    await userEvent.click(screen.getByText(/Créer une offre/))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: OFFER_FORM_NAVIGATION_IN.VENUE,
        to: OFFER_FORM_HOMEPAGE,
        used: OFFER_FORM_NAVIGATION_MEDIUM.VENUE_BUTTON,
        isEdition: false,
      }
    )
  })
})
