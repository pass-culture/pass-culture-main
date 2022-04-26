import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { apiV1 } from 'api/api'
import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import {
  getOfferInputForField,
  setOfferValues,
  sidebarDisplayed,
} from '../helpers'

import {
  categories,
  offerer1,
  offerer2,
  offerer2VenueVirtual,
  offerer2VenuePhysicalAccessible,
  venueVirtual,
  venuePhysicalAccessible,
  venuePhysicalUndefinedAccessibility,
} from './mocks'

jest.mock('repository/pcapi/pcapi', () => ({
  createOffer: jest.fn(),
  getUserValidatedOfferersNames: jest.fn(),
  getVenue: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadCategories: jest.fn(),
}))

const renderOffer = async (props, store, pathname, queryParams = null) => {
  const rtlRenderReturn = render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[{ pathname: pathname, search: queryParams }]}
      >
        <Route
          path={[
            '/offre/creation/individuel',
            '/offre/:offerId([A-Z0-9]+)/individuel',
            '/offre/:offerId([A-Z0-9]+)/individuel/edition',
          ]}
        >
          <>
            <OfferLayout {...props} />
            <NotificationContainer />
          </>
        </Route>
      </MemoryRouter>
    </Provider>
  )

  await getOfferInputForField('categoryId')

  return rtlRenderReturn
}

const renderOfferCreation = async ({
  props,
  store,
  subCategory,
  offererId = null,
  venueId = null,
}) => {
  let queryParams = null
  if (offererId || venueId) queryParams = {}
  if (offererId) queryParams.structure = offererId
  if (venueId) queryParams.lieu = venueId
  if (queryParams !== null)
    queryParams = new URLSearchParams(queryParams).toString()

  const rtlRenderReturn = await renderOffer(
    props,
    store,
    '/offre/creation/individuel',
    queryParams
  )
  setOfferValues({ categoryId: subCategory.categoryId })
  await getOfferInputForField('subcategoryId')
  setOfferValues({ subcategoryId: subCategory.id })
  await sidebarDisplayed()
  if (venueId) {
    await screen.findByText('Où ?')
  }

  return rtlRenderReturn
}

const renderOfferEdition = async ({ props, store, offerId }) => {
  const rtlRenderReturn = await renderOffer(
    props,
    store,
    `/offre/${offerId}/individuel/edition`
  )
  await sidebarDisplayed()
  return rtlRenderReturn
}

export const initialize = async ({
  offer = null,
  selectedSubcategoryId = null,
  selectedVenue = null,
  selectedVenueFromUrl = null,
}) => {
  if (
    selectedVenue === null &&
    selectedVenueFromUrl === null &&
    offer === null
  ) {
    throw Error(
      'Test initialize() need a "offer", a"selectedVenue" or a "selectedVenueFromUrl" argument.'
    )
  }

  const store = configureTestStore({
    data: {
      users: [
        {
          publicName: 'François',
          isAdmin: false,
          email: 'francois@example.com',
        },
      ],
    },
  })

  pcapi.getUserValidatedOfferersNames.mockResolvedValue([offerer1, offerer2])
  pcapi.getVenuesForOfferer.mockResolvedValue([
    venueVirtual,
    venuePhysicalUndefinedAccessibility,
    venuePhysicalAccessible,
    offerer2VenueVirtual,
    offerer2VenuePhysicalAccessible,
  ])
  pcapi.createOffer.mockResolvedValue({})
  pcapi.loadCategories.mockResolvedValue(categories)

  let rtlRenderReturn
  if (offer) {
    jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(offer)
    pcapi.getVenue.mockReturnValue(offer.venue)
    rtlRenderReturn = await renderOfferEdition({
      props: {},
      store,
      offerId: offer.id,
    })
  } else {
    if (selectedSubcategoryId === null) {
      throw Error(
        'initialize() for creation need "selectedSubcategory" argument'
      )
    }
    const selectedSubcategory = categories.subcategories.find(
      subCategory => subCategory.id === selectedSubcategoryId
    )

    pcapi.getVenue.mockReturnValue(
      selectedVenue ? selectedVenue : selectedVenueFromUrl
    )

    rtlRenderReturn = await renderOfferCreation({
      props: {},
      store,
      subCategory: selectedSubcategory,
      offererId: selectedVenueFromUrl
        ? selectedVenueFromUrl.managingOffererId
        : null,
      venueId: selectedVenueFromUrl ? selectedVenueFromUrl.id : null,
    })
  }

  if (selectedVenue) {
    setOfferValues({
      offererId: selectedVenue.managingOffererId,
      venueId: selectedVenue.id,
    })
    await screen.findByText('Où ?')
  }

  return rtlRenderReturn
}
