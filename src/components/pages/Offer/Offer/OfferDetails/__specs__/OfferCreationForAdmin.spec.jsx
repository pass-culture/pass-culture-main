import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import NotificationV2Container from 'components/layout/NotificationV2/NotificationV2Container'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferLayoutContainer from '../../OfferLayoutContainer'

import { setOfferValues } from './helpers'

jest.mock('repository/pcapi/pcapi', () => ({
  createOffer: jest.fn(),
  getOfferer: jest.fn(),
  getValidatedOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  getVenue: jest.fn(),
  loadTypes: jest.fn(),
}))

const renderOffers = async (props, store, queryParams = null) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[{ pathname: '/offres/creation', search: queryParams }]}>
          <Route path="/offres/">
            <>
              <OfferLayoutContainer {...props} />
              <NotificationV2Container />
            </>
          </Route>
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('offerDetails - Creation - admin user', () => {
  let types
  let offerer
  let props
  let store
  let venues

  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: true }] } })
    props = {
      setShowThumbnailForm: jest.fn(),
    }
    types = [
      {
        conditionalFields: ['author', 'visa', 'stageDirector'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Cinéma - projections et autres évènements',
        type: 'Event',
        value: 'EventType.CINEMA',
      },
    ]
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
    pcapi.loadTypes.mockResolvedValue(types)
    pcapi.getOfferer.mockResolvedValue(offerer)
    pcapi.getVenue.mockReturnValue(Promise.resolve())
    jest.spyOn(window, 'scrollTo').mockImplementation()
  })

  afterEach(() => {
    pcapi.createOffer.mockClear()
    pcapi.getValidatedOfferers.mockClear()
    pcapi.getVenuesForOfferer.mockClear()
    pcapi.loadTypes.mockClear()
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
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByDisplayValue(offerer.name)).toBeInTheDocument()
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
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByDisplayValue(venues[0].name)).toBeInTheDocument()
      })
    })
  })
})
