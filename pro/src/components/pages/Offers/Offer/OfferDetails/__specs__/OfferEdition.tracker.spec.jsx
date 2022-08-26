import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import * as useAnalytics from 'components/hooks/useAnalytics'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import { Events } from 'core/FirebaseEvents/constants'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import { fieldLabels } from './helpers'

window.open = jest.fn()
const mockLogEvent = jest.fn()

jest.mock('repository/pcapi/pcapi', () => ({
  getVenuesForOfferer: jest.fn(),
  getVenue: jest.fn(),
  loadCategories: jest.fn(),
  loadStocks: jest.fn(),
  postThumbnail: jest.fn(),
  updateOffer: jest.fn(),
}))

const renderOffers = async (props, store, queryParams = '') => {
  const rtlUtils = render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/offre/ABC12/individuel/edition',
            search: queryParams,
          },
        ]}
      >
        <Route path="/offre/:offerId([A-Z0-9]+)/individuel">
          <OfferLayout {...props} />
        </Route>
      </MemoryRouter>
    </Provider>
  )

  await screen.findByLabelText(fieldLabels.categoryId.label, {
    exact: fieldLabels.categoryId.exact,
  })

  return rtlUtils
}

describe('offerDetails - Edition', () => {
  let editedOffer
  let venueManagingOfferer
  let store
  let editedOfferVenue
  let categories

  beforeEach(() => {
    store = configureTestStore({
      user: {
        currentUser: {
          publicName: 'François',
          isAdmin: false,
          email: 'francois@example.com',
        },
      },
    })

    venueManagingOfferer = {
      id: 'BA',
      name: 'La structure',
    }

    editedOfferVenue = {
      id: 'AB',
      isVirtual: false,
      managingOfferer: venueManagingOfferer,
      managingOffererId: venueManagingOfferer.id,
      name: 'Le lieu',
      offererName: 'La structure',
      bookingEmail: 'venue@example.com',
      withdrawalDetails: null,
      audioDisabilityCompliant: null,
      mentalDisabilityCompliant: null,
      motorDisabilityCompliant: null,
      visualDisabilityCompliant: null,
    }

    editedOffer = {
      id: 'ABC12',
      nonHumanizedId: 111,
      subcategoryId: 'ID',
      name: 'My edited offer',
      venue: editedOfferVenue,
      venueId: editedOfferVenue.id,
      thumbUrl: null,
      description: 'My edited description',
      withdrawalDetails: 'My edited withdrawal details',
      status: 'SOLD_OUT',
      extraData: {
        musicType: '501',
        musicSubType: '502',
        isbn: '1234567890123',
      },
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      visualDisabilityCompliant: false,
    }

    categories = {
      categories: [
        {
          id: 'ID',
          name: 'Musique',
          proLabel: 'Musique',
          appLabel: 'Musique',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: 'ID',
          name: 'Musique SubCat 1',
          categoryId: 'ID',
          isEvent: false,
          isDigital: false,
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          proLabel: 'Musique SubCat 1',
          appLabel: 'Musique SubCat 1',
          conditionalFields: ['author', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: true,
          canBeEducational: true,
          isSelectable: true,
        },
      ],
    }

    jest.spyOn(api, 'getOffer').mockResolvedValue(editedOffer)
    pcapi.loadCategories.mockResolvedValue(categories)
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track when clicking on view in app link', async () => {
    // Given
    await renderOffers({}, store)
    const previewLink = await screen.findByText('Visualiser dans l’app', {
      selector: 'a',
    })
    expect(previewLink).toBeInTheDocument()

    // When
    await userEvent.click(previewLink)

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'details',
        isEdition: true,
        to: 'AppPreview',
        used: 'DetailsPreview',
      }
    )
  })
})
