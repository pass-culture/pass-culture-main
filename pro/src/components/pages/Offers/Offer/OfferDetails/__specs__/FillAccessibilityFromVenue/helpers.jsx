import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { MemoryRouter, Route } from 'react-router-dom'
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
import {
  getOfferInputForField,
  setOfferValues,
  sidebarDisplayed,
} from '../helpers'
import { render, within } from '@testing-library/react'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import { Provider } from 'react-redux'
import React from 'react'
import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

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
    jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
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
    const selectedCategory = categories.categories.find(
      category => category.id === selectedSubcategory.categoryId
    )

    pcapi.getVenue.mockReturnValue(
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
