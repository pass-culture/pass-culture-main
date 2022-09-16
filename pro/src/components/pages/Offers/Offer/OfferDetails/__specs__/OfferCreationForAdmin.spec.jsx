import '@testing-library/jest-dom'

import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import Notification from 'components/layout/Notification/Notification'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferLayout from '../../OfferLayout'

import { setOfferValues } from './helpers'

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferer: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  getVenue: jest.fn(),
  loadCategories: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    postOffer: jest.fn(),
  },
}))

const renderOffers = async (props, store, queryParams = null) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter
          initialEntries={[
            { pathname: '/offre/creation/individuel', search: queryParams },
          ]}
        >
          <Route path="/offre/">
            <>
              <OfferLayout {...props} />
              <Notification />
            </>
          </Route>
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('offerDetails - Creation - admin user', () => {
  let categories
  let offerer
  let props
  let store
  let venues

  beforeEach(() => {
    store = configureTestStore({
      user: {
        currentUser: {
          publicName: 'François',
          isAdmin: true,
          email: 'toto@tata.com',
        },
      },
    })

    props = {
      setShowThumbnailForm: jest.fn(),
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
          canBeDuo: false,
          isSelectable: true,
        },
      ],
    }

    const offererId = 'BA'

    venues = [
      {
        id: 'AB',
        isVirtual: false,
        managingOffererId: offererId,
        name: 'Le lieu',
        offererName: 'La structure',
      },
    ]

    offerer = {
      id: offererId,
      name: 'La structure',
      managedVenues: venues,
    }

    pcapi.loadCategories.mockResolvedValue(categories)
    pcapi.getOfferer.mockResolvedValue(offerer)
    pcapi.getVenue.mockReturnValue(Promise.resolve())
    jest.spyOn(window, 'scrollTo').mockImplementation()
  })

  describe('render when creating a new offer as admin', () => {
    it('should get selected offerer from API', async () => {
      // When
      await renderOffers(props, store, `?structure=${offerer.id}`)

      // Then
      expect(pcapi.getOfferer).toHaveBeenLastCalledWith(offerer.id)
    })

    it('should not get venues from API', async () => {
      // When
      await renderOffers(props, store, `?structure=${offerer.id}`)

      // Then
      expect(pcapi.getVenuesForOfferer).toHaveBeenCalledTimes(0)
    })

    describe('when selecting an offer type', () => {
      it('should have offerer selected and select disabled', async () => {
        // Given
        await renderOffers(props, store, `?structure=${offerer.id}`)

        // When
        await setOfferValues({ categoryId: 'ID' })
        await setOfferValues({ subcategoryId: 'ID' })

        // Then
        expect(
          await screen.findByDisplayValue(offerer.name)
        ).toBeInTheDocument()
        expect(screen.getByDisplayValue(offerer.name)).toBeDisabled()
      })

      it('should have venue selected when given as queryParam', async () => {
        // Given
        await renderOffers(
          props,
          store,
          `?lieu=${venues[0].id}&structure=${venues[0].managingOffererId}`
        )

        // When
        await setOfferValues({ categoryId: 'ID' })
        await setOfferValues({ subcategoryId: 'ID' })

        // Then
        expect(
          await screen.findByDisplayValue(venues[0].name)
        ).toBeInTheDocument()
      })
    })
  })
})
