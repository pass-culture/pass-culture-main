import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OfferStatus } from 'apiClient/v2'
import Notification from 'components/Notification/Notification'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { IOfferIndividual } from 'core/Offers/types'
import * as useAnalytics from 'hooks/useAnalytics'
import { RootState } from 'store/reducers'
import { renderWithProviders } from 'utils/renderWithProviders'

import Confirmation from '../Confirmation'

const mockLogEvent = jest.fn()
window.open = jest.fn()

jest.mock('utils/config', () => {
  return {
    WEBAPP_URL: 'http://localhost',
  }
})

const renderOffer = (
  contextOverride: Partial<IOfferIndividualContext>,
  storeOverride?: Partial<RootState>
) => {
  const contextValue: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    ...storeOverride,
  }

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path="/confirmation"
          element={
            <OfferIndividualContext.Provider value={contextValue}>
              <Confirmation />
            </OfferIndividualContext.Provider>
          }
        />
      </Routes>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: ['/confirmation'] }
  )
}

describe('Confirmation', () => {
  let store: any
  let contextOverride: Partial<IOfferIndividualContext>
  let offer: IOfferIndividual
  const venueId = 45
  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          isAdmin: false,
          email: 'email@example.com',
        },
      },
    }
    offer = {
      nonHumanizedId: 12,
      venueId: venueId,
      venue: {
        offerer: {
          id: 'OFID',
          name: 'Offerer name',
        },
      },
      status: OfferStatus.ACTIVE,
    } as IOfferIndividual
    contextOverride = {
      offer: offer,
    }
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })

  it('should display a pending message when offer is pending for validation', () => {
    offer.status = OfferStatus.PENDING
    renderOffer(contextOverride, store)
    expect(screen.getByText('Offre en cours de validation')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `http://localhost/offre/${offer.nonHumanizedId}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute('href', `/offre/creation?structure=OFID&lieu=${venueId}`)
    expect(
      screen.getByText('Voir la liste des offres', { selector: 'a' })
    ).toHaveAttribute('href', `/offres`)
  })

  it('should display a success message when offer is accepted', () => {
    renderOffer(contextOverride, store)
    expect(screen.getByText('Offre publiée !')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `http://localhost/offre/${offer.nonHumanizedId}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute('href', `/offre/creation?structure=OFID&lieu=${venueId}`)
  })

  describe('trackers', () => {
    it('should track when clicking on see offer', async () => {
      renderOffer(contextOverride, store)

      await userEvent.click(
        screen.getByText('Visualiser l’offre dans l’application', {
          selector: 'a',
        })
      )

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'confirmation',
          isEdition: false,
          to: 'AppPreview',
          used: 'ConfirmationPreview',
        }
      )
    })

    it('should track when clicking on create new offer', async () => {
      renderOffer(contextOverride, store)

      await userEvent.click(
        screen.getByText('Créer une nouvelle offre', {
          selector: 'a',
        })
      )

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'confirmation',
          isEdition: false,
          to: 'OfferFormHomepage',
          used: 'ConfirmationButtonNewOffer',
        }
      )
    })

    it('should track when clicking on see offers list', async () => {
      renderOffer(contextOverride, store)

      await userEvent.click(
        screen.getByText('Voir la liste des offres', {
          selector: 'a',
        })
      )

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'confirmation',
          isEdition: false,
          to: 'Offers',
          used: 'ConfirmationButtonOfferList',
        }
      )
    })
  })
})
