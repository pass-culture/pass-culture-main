import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OfferStatus } from 'apiClient/v2'
import Notification from 'components/Notification/Notification'
import {
  OfferIndividualContextValues,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OfferIndividual } from 'core/Offers/types'
import * as useAnalytics from 'hooks/useAnalytics'
import { RootState } from 'store/reducers'
import { renderWithProviders } from 'utils/renderWithProviders'

import Confirmation from '../Confirmation'

const mockLogEvent = vi.fn()
window.open = vi.fn()

vi.mock('utils/config', async () => {
  return {
    ...((await vi.importActual('utils/config')) ?? {}),
    WEBAPP_URL: 'https://localhost',
  }
})

const renderOffer = (
  contextOverride: Partial<OfferIndividualContextValues>,
  storeOverride?: Partial<RootState>
) => {
  const contextValue: OfferIndividualContextValues = {
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
  let contextOverride: Partial<OfferIndividualContextValues>
  let offer: OfferIndividual
  const venueId = 45
  const offererId = 51
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
      id: 12,
      venueId: venueId,
      venue: {
        offerer: {
          id: offererId,
          name: 'Offerer name',
        },
      },
      status: OfferStatus.ACTIVE,
    } as OfferIndividual
    contextOverride = {
      offer: offer,
    }
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should display a pending message when offer is pending for validation', () => {
    offer.status = OfferStatus.PENDING
    renderOffer(contextOverride, store)
    expect(screen.getByText('Offre en cours de validation')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `https://localhost/offre/${offer.id}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation?structure=${offererId}&lieu=${venueId}`
    )
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
    ).toHaveAttribute('href', `https://localhost/offre/${offer.id}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation?structure=${offererId}&lieu=${venueId}`
    )
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
