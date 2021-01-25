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
  getValidatedOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  getVenue: jest.fn(),
  loadTypes: jest.fn(),
}))

const renderOffers = async (props, store, queryParams = null) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[{ pathname: '/offres/v2/creation', search: queryParams }]}>
          <Route path="/offres/v2/">
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
  let offerers
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
    const offerer1Id = 'BA'
    const offerer2Id = 'BAC'
    offerers = [
      {
        id: offerer1Id,
        name: 'La structure',
      },
      {
        id: offerer2Id,
        name: "L'autre structure",
      },
    ]
    venues = [
      {
        id: 'AB',
        isVirtual: false,
        managingOffererId: offerer1Id,
        name: 'Le lieu',
        offererName: 'La structure',
      },
      {
        id: 'ABC',
        isVirtual: false,
        managingOffererId: offerer2Id,
        name: "L'autre lieu",
        offererName: "L'autre structure",
      },
      {
        id: 'ABCD',
        isVirtual: true,
        managingOffererId: offerer2Id,
        name: "L'autre lieu (Offre numérique)",
        offererName: "L'autre structure",
      },
    ]
    pcapi.loadTypes.mockResolvedValue(types)
    pcapi.getValidatedOfferers.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockImplementation(offererId =>
      Promise.resolve(venues.filter(venue => venue.managingOffererId === offererId))
    )
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
    it('should get offerers from API', async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(pcapi.getValidatedOfferers).toHaveBeenCalledTimes(1)
    })

    it('should not get venues from API when no offererId was provided', async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(pcapi.getVenuesForOfferer).toHaveBeenCalledTimes(0)
    })

    it('should get venues of provided offererId from API', async () => {
      // When
      await renderOffers(props, store, `?structure=${offerers[0].id}`)

      // Then
      expect(pcapi.getVenuesForOfferer).toHaveBeenLastCalledWith(offerers[0].id)
    })

    describe('when selecting an offer type', () => {
      it('should have offerer selected when given as queryParam', async () => {
        // Given
        await renderOffers(props, store, `?structure=${offerers[0].id}`)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
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

      it('should remove venues when unselecting offerer', async () => {
        // Given
        await renderOffers(props, store, `?structure=${offerers[0].id}`)
        await setOfferValues({ type: 'EventType.CINEMA' })

        // When
        await setOfferValues({ offererId: '' })

        // Then
        expect(screen.queryByText(venues[0].name)).not.toBeInTheDocument()
        expect(screen.queryByText(venues[1].name)).not.toBeInTheDocument()
        expect(screen.queryByText(venues[2].name)).not.toBeInTheDocument()
      })
    })
  })
})
