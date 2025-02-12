import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'


import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import { GET_OFFERER_HEADLINE_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import * as useNotification from 'commons/hooks/useNotification'
import {
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY,
  IndividualOffersContextProvider,
  IndividualOffersContextProviderProps,
  useIndividualOffersContext
} from "./IndividualOffersContext"

const LABELS = {
  display: {
    headlineOffer: 'Headline Offer Id',
    isHeadlineOfferAllowedForOfferer: 'Is Headline Offer Allowed For Offerer',
    isHeadlineOfferBannerOpen: 'Is Headline Offer Banner Open',
  },
  controls: {
    upsertHeadlineOffer: 'Upsert Headline Offer',
    removeHeadlineOffer: 'Delete Headline Offer',
    closeHeadlineOfferBanner: 'Close Headline Offer Banner',
  },
  notify: {
    upsert: {
      success: 'Votre offre a été mise à la une !',
      error: 'Une erreur s’est produite lors de l’ajout de votre offre à la une',
    },
    delete: {
      success: 'Votre offre n’est plus à la une',
      error: 'Une erreur s’est produite lors du retrait de votre offre à la une',
    }
  }
}

const MOCK_DATA = {
  offerer: currentOffererFactory(),
  headlineOffer: {
    id: 1,
    name: 'Offre à la une',
    venueId: 1,
  },
  newHeadlineOffer: {
    id: 2,
    name: 'Nouvelle offre à la une',
    venueId: 1,
  }
}

vi.mock('apiClient/api', () => ({
  api: {
    getOffererHeadlineOffer: vi.fn(),
    upsertHeadlineOffer: vi.fn(),
    deleteHeadlineOffer: vi.fn(),
  }
}))

const mockMutate = vi.fn()
vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: vi.fn(() => ({
    mutate: mockMutate,
  })),
}))

const TestComponent = () => {
  const {
    headlineOffer,
    upsertHeadlineOffer,
    removeHeadlineOffer,
    isHeadlineOfferBannerOpen,
    closeHeadlineOfferBanner,
    isHeadlineOfferAllowedForOfferer,
  } = useIndividualOffersContext()

  return <>
    <h1>Test Component</h1>
    <div id="display">
      <span>{LABELS.display.headlineOffer}: {headlineOffer ? headlineOffer.id : 'null'}</span>
      <span>{LABELS.display.isHeadlineOfferAllowedForOfferer}: {isHeadlineOfferAllowedForOfferer ? 'true' : 'false'}</span>
      <span>{LABELS.display.isHeadlineOfferBannerOpen}: {isHeadlineOfferBannerOpen ? 'true' : 'false'}</span>
    </div>
    <div id="controls">
      <button onClick={() => upsertHeadlineOffer({
        offerId: MOCK_DATA.newHeadlineOffer.id,
        context: { actionType: 'add' }
      })}>{LABELS.controls.upsertHeadlineOffer}</button>
      <button onClick={removeHeadlineOffer}>{LABELS.controls.removeHeadlineOffer}</button>
      <button onClick={closeHeadlineOfferBanner}>{LABELS.controls.closeHeadlineOfferBanner}</button>
    </div>
  </>
}

type IndividualOffersContextProviderTestProps = Partial<IndividualOffersContextProviderProps> & {
  isFeatureEnabled?: boolean
}

const renderIndividualOffersContext = ({
  isFeatureEnabled = true,
  isHeadlineOfferAllowedForOfferer = true
}: IndividualOffersContextProviderTestProps = {}) => {
  return renderWithProviders(
    <IndividualOffersContextProvider
      isHeadlineOfferAllowedForOfferer={isHeadlineOfferAllowedForOfferer}
    >
      <TestComponent />
    </IndividualOffersContextProvider>, 
    {
      features: [
        ...(isFeatureEnabled ? ['WIP_HEADLINE_OFFER'] : [])
      ],
       storeOverrides: {
        offerer: MOCK_DATA.offerer,
      },
    }
  )
}

describe('IndividualOffersContext', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererHeadlineOffer').mockResolvedValue(MOCK_DATA.headlineOffer)
    localStorage.clear()
  })

  describe('should tell if headline offer is available as a feature', () => {
    // FIXME: isHeadlineOfferAvailable as a combination of
    // isHeadlineOfferAllowedForOfferer and isFeatureEnabled should be 
    // exported instead of isHeadlineOfferAllowedForOfferer alone.
    // it('should be available if feature is enabled and offerer is allowed to use it', () => {})
    // it('should not be available if feature is disabled', () => {})
    // it('should not be available if offerer is not allowed to use it', () => {})
  
    // FIXME: we would like to manage isHeadlineOfferAllowedForOfferer in
    // the context itself. This test should be rewritten.
    it('should be available if offerer is allowed to use it', async () => {
      renderIndividualOffersContext({ isHeadlineOfferAllowedForOfferer: true })

      const display = await screen.findByText(new RegExp(LABELS.display.isHeadlineOfferAllowedForOfferer))
      expect(display).toBeTruthy()
    })
  })

  it('should fetch headline offer and make it available', async () => {
    renderIndividualOffersContext()

    const display = await screen.findByText(new RegExp(LABELS.display.headlineOffer))
    expect(display.textContent).toContain(MOCK_DATA.headlineOffer.id)
  })

  describe('upsertHeadlineOffer', () => {
    it('should upsert headline offer and update state', async () => {
      renderIndividualOffersContext()

      const upsertButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.upsertHeadlineOffer)
      })
      await userEvent.click(upsertButton)

      await waitFor(() => {
        expect(api.upsertHeadlineOffer).toHaveBeenCalledWith({
          offerId: MOCK_DATA.newHeadlineOffer.id
        })
      })

      // We are not testing display update since this happens after a re-render,
      // which is triggered by the SWR mutate function on GET_OFFERER_HEADLINE_OFFER_QUERY_KEY.
      // This would be like testing the SWR library itself & its none of our concern.
      // Yet, we expect the mutation to be called.
      expect(mockMutate).toHaveBeenCalledWith([
        GET_OFFERER_HEADLINE_OFFER_QUERY_KEY,
        MOCK_DATA.offerer.selectedOffererId
      ])
    })

    describe('about notifications', () => {
      it('should notify success on successful upsert', async () => {
        let notifySuccess = vi.fn()
        vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
          success: notifySuccess,
          error: vi.fn(),
          information: vi.fn(),
          pending: vi.fn(),
          close: vi.fn(),
        }))

        renderIndividualOffersContext()
  
        const upsertButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.upsertHeadlineOffer)
        })
        await userEvent.click(upsertButton)
  
        expect(notifySuccess).toHaveBeenCalledWith(LABELS.notify.upsert.success)
      })

      it('should notify error on failed upsert', async () => {
        let notifyError = vi.fn()
        vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
          success: vi.fn(),
          error: notifyError,
          information: vi.fn(),
          pending: vi.fn(),
          close: vi.fn(),
        }))
        vi.spyOn(api, 'upsertHeadlineOffer').mockRejectedValue('PLONK')

        renderIndividualOffersContext()

        const upsertButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.upsertHeadlineOffer)
        })
        await userEvent.click(upsertButton)

        expect(notifyError).toHaveBeenCalledWith(LABELS.notify.upsert.error)
      })
    })
  
    it('should log event on successful upsert', async () => {
      let logEvent = vi.fn()
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent
      }))

      renderIndividualOffersContext()

      const upsertButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.upsertHeadlineOffer)
      })
      await userEvent.click(upsertButton)

      expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER, {
        from: '/',
        actionType: 'add',
        requiredImageUpload: false,
      })
    })

    it('should close headline offer banner on successful upsert', async () => {
      renderIndividualOffersContext()

      const display = await screen.findByText(new RegExp(LABELS.display.isHeadlineOfferBannerOpen))
      expect(display.textContent).toContain('true')

      const upsertButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.upsertHeadlineOffer)
      })
      await userEvent.click(upsertButton)

      await waitFor(async () => {
        const updatedDisplay = await screen.findByText(new RegExp(LABELS.display.isHeadlineOfferBannerOpen))
        expect(updatedDisplay.textContent).toContain('false')
      })
    })
  })

  describe('removeHeadlineOffer', () => {
    it('should remove headline offer and update state', async () => {
      renderIndividualOffersContext()

      const removeButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.removeHeadlineOffer)
      })
      await userEvent.click(removeButton)

      await waitFor(() => {
        expect(api.deleteHeadlineOffer).toHaveBeenCalled()
      })

      // We are not testing display update since this happens after a re-render,
      // which is triggered by the SWR mutate function on GET_OFFERER_HEADLINE_OFFER_QUERY_KEY.
      // This would be like testing the SWR library itself & its none of our concern.
      // Yet, we expect the mutation to be called.
      expect(mockMutate).toHaveBeenCalledWith([
        GET_OFFERER_HEADLINE_OFFER_QUERY_KEY,
        MOCK_DATA.offerer.selectedOffererId
      ])
    })

    describe('about notifications', () => {
      it('should notify success on successful removal', async () => {
        let notifySuccess = vi.fn()
        vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
          success: notifySuccess,
          error: vi.fn(),
          information: vi.fn(),
          pending: vi.fn(),
          close: vi.fn(),
        }))

        renderIndividualOffersContext()

        const removeButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.removeHeadlineOffer)
        })
        await userEvent.click(removeButton)

        expect(notifySuccess).toHaveBeenCalledWith(LABELS.notify.delete.success)
      })

      it('should notify error on failed removal', async () => {
        let notifyError = vi.fn()
        vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
          success: vi.fn(),
          error: notifyError,
          information: vi.fn(),
          pending: vi.fn(),
          close: vi.fn(),
        }))
        vi.spyOn(api, 'deleteHeadlineOffer').mockRejectedValue('PLONK')

        renderIndividualOffersContext()

        const removeButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.removeHeadlineOffer)
        })
        await userEvent.click(removeButton)

        expect(notifyError).toHaveBeenCalledWith(LABELS.notify.delete.error)
      })
    })
  
    it('should log event on successful removal', async () => {
      let logEvent = vi.fn()
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent
      }))

      renderIndividualOffersContext()

      const removeButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.removeHeadlineOffer)
      })
      await userEvent.click(removeButton)

      expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER, {
        from: '/',
        actionType: 'delete',
      })
    })
  })

  describe('closeHeadlineOfferBanner', () => {
    it('should close headline offer banner and update state', async () => {
      renderIndividualOffersContext()

      await waitFor(async () => {
        const display = await screen.findByText(new RegExp(LABELS.display.isHeadlineOfferBannerOpen))
        expect(display.textContent).toContain('true')
      })

      const closeButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.closeHeadlineOfferBanner)
      })
      await userEvent.click(closeButton)

      await waitFor(async () => {
        const updatedDisplay = await screen.findByText(new RegExp(LABELS.display.isHeadlineOfferBannerOpen))
        expect(updatedDisplay.textContent).toContain('false')
      })
    })
  
    it('should remember the user choice', async () => {
      renderIndividualOffersContext()

      expect(localStorage.getItem(LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY)).toBeNull()

      const closeButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.closeHeadlineOfferBanner)
      })
      await userEvent.click(closeButton)

      expect(localStorage.getItem(LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY)).toBe('true')
    })
  })
})