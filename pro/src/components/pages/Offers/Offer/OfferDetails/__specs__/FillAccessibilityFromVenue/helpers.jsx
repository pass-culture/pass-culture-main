import '@testing-library/jest-dom'

import { render, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router-dom'

import { api } from 'apiClient/api'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import { Notification } from 'new_components/Notification'
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
  offerer2VenuePhysicalAccessible,
  offerer2VenueVirtual,
  venuePhysicalAccessible,
  venuePhysicalUndefinedAccessibility,
  venueVirtual,
} from './mocks'

jest.mock('apiClient/api', () => ({
  api: {
    postOffer: jest.fn(),
    getOffer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenues: jest.fn(),
    getVenue: jest.fn(),
    getCategories: jest.fn(),
  },
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
            <Notification />
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
  categoryName,
  subCategoryName,
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
  const categorySelect = await getOfferInputForField('categoryId')
  await userEvent.selectOptions(categorySelect, categoryName)
  const subCategorySelect = await getOfferInputForField('subcategoryId')
  await userEvent.selectOptions(subCategorySelect, subCategoryName)

  const sidebar = await sidebarDisplayed()
  if (venueId) {
    await within(sidebar).findByText('Où ?')
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
      'Test initialize() need a "offer", a "selectedVenue" or a "selectedVenueFromUrl" argument.'
    )
  }

  const store = configureTestStore({
    user: {
      currentUser: {
        publicName: 'François',
        isAdmin: false,
        email: 'francois@example.com',
      },
    },
  })

  api.listOfferersNames.mockResolvedValue({
    offerersNames: [offerer1, offerer2],
  })
  api.getVenues.mockResolvedValue({
    venues: [
      venueVirtual,
      venuePhysicalUndefinedAccessibility,
      venuePhysicalAccessible,
      offerer2VenueVirtual,
      offerer2VenuePhysicalAccessible,
    ],
  })
  api.postOffer.mockResolvedValue({})
  api.getCategories.mockResolvedValue(categories)

  let rtlRenderReturn
  if (offer) {
    jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
    api.getVenue.mockReturnValue(offer.venue)
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
    const selectedCategory = categories.categories.find(
      category => category.id === selectedSubcategory.categoryId
    )

    api.getVenue.mockReturnValue(
      selectedVenue ? selectedVenue : selectedVenueFromUrl
    )

    rtlRenderReturn = await renderOfferCreation({
      props: {},
      store,
      categoryName: selectedCategory.proLabel,
      subCategoryName: selectedSubcategory.proLabel,
      offererId: selectedVenueFromUrl
        ? selectedVenueFromUrl.managingOffererId
        : null,
      venueId: selectedVenueFromUrl
        ? selectedVenueFromUrl.id
        : selectedVenue.id,
    })
  }

  if (selectedVenue) {
    await setOfferValues({
      offererId: selectedVenue.managingOffererId,
      venueId: selectedVenue.id,
    })
    const sidebar = await sidebarDisplayed()
    if (!selectedVenue.isVirtual) {
      await within(sidebar).findByText('Où ?')
    }
  }

  return rtlRenderReturn
}
