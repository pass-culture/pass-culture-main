import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import VenueEditon from '../VenueEdition'

const mockLogEvent = jest.fn()

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: 'BQ',
    venueId: 'AQ',
  }),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  createVenueProvider: jest.fn(),
  getBusinessUnits: jest.fn().mockResolvedValue([]),
  loadProviders: jest.fn().mockResolvedValue([]),
  loadVenueProviders: jest.fn().mockResolvedValue([]),
  getOfferer: jest.fn().mockResolvedValue({}),
  getVenueTypes: jest.fn().mockResolvedValue([]),
  getVenueLabels: jest.fn().mockResolvedValue([]),
  editVenue: jest.fn(),
  canOffererCreateEducationalOffer: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getVenue: jest.fn(),
  },
}))

const renderVenueEdition = () => {
  const store = configureTestStore()

  return render(
    <Provider store={store}>
      <MemoryRouter>
        <VenueEditon />
      </MemoryRouter>
    </Provider>
  )
}

const venue = {
  noDisabilityCompliant: false,
  isAccessibilityAppliedOnAllOffers: true,
  audioDisabilityCompliant: true,
  mentalDisabilityCompliant: true,
  motorDisabilityCompliant: true,
  visualDisabilityCompliant: true,
  address: '1 boulevard Poissonnière',
  bookingEmail: 'fake@example.com',
  city: 'Paris',
  dateCreated: '2021-09-13T14:59:21.661969Z',
  dateModifiedAtLastProvider: '2021-09-13T14:59:21.661955Z',
  departementCode: '75',
  id: 'AQ',
  isBusinessUnitMainVenue: false,
  isValidated: true,
  isVirtual: false,
  isPermanent: true,
  latitude: 48.91683,
  longitude: 2.43884,
  managingOffererId: 'AM',
  nOffers: 7,
  name: 'Maison de la Brique',
  postalCode: '75000',
  publicName: 'Maison de la Brique',
  siret: '22222222311111',
  venueTypeCode: 'DE',
  businessUnit: { id: 20 },
  businessUnitId: 20,
  contact: {
    email: 'contact@venue.com',
    website: 'https://my@website.com',
    phoneNumber: '+33102030405',
  },
}

describe('create new offer link', () => {
  it('should track when clicking to offer link', async () => {
    // given
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    api.getVenue.mockResolvedValue({ ...venue, id: 'CM' })
    renderVenueEdition()

    // when
    const createOfferLink = await screen.findByRole('link', {
      name: /Créer une offre/,
    })
    await userEvent.click(createOfferLink)

    // then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Venue',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'VenueButton',
      }
    )
  })
})
