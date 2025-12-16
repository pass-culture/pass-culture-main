import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { currentOffererFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  HeadlineOfferContextProvider,
  useHeadlineOfferContext,
} from './HeadlineOfferContext'

const LABELS = {
  display: {
    headlineOffer: 'Headline Offer Id',
    isHeadlineOfferAllowedForOfferer: 'Is Headline Offer Available',
  },
  controls: {
    upsertHeadlineOffer: 'Upsert Headline Offer',
    removeHeadlineOffer: 'Delete Headline Offer',
  },
  notify: {
    upsert: {
      success: 'Votre offre a été mise à la une !',
      error:
        'Une erreur s’est produite lors de l’ajout de votre offre à la une',
    },
    delete: {
      success: 'Votre offre n’est plus à la une',
      error:
        'Une erreur s’est produite lors du retrait de votre offre à la une',
    },
  },
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
  },
  otherVenueOffer: {
    id: 3,
    name: 'Offre sur autre venue',
    venueId: 2,
  },
}

vi.mock('@/apiClient/api', () => ({
  api: {
    getOffererHeadlineOffer: vi.fn(),
    upsertHeadlineOffer: vi.fn(),
    deleteHeadlineOffer: vi.fn(),
    getVenues: vi.fn(),
  },
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
    isHeadlineOfferAllowedForOfferer,
  } = useHeadlineOfferContext()

  return (
    <>
      <h1>Test Component</h1>
      <div>
        <span>
          {LABELS.display.headlineOffer}:{' '}
          {headlineOffer ? headlineOffer.id : 'null'}
        </span>
        <span>
          {LABELS.display.isHeadlineOfferAllowedForOfferer}:{' '}
          {isHeadlineOfferAllowedForOfferer ? 'true' : 'false'}
        </span>
      </div>
      <div>
        <button
          onClick={() =>
            upsertHeadlineOffer({
              offerId: MOCK_DATA.newHeadlineOffer.id,
              context: { actionType: 'add' },
            })
          }
        >
          {LABELS.controls.upsertHeadlineOffer}
        </button>
        <button onClick={removeHeadlineOffer}>
          {LABELS.controls.removeHeadlineOffer}
        </button>
      </div>
    </>
  )
}

const renderIndividualOffersContext = () => {
  return renderWithProviders(
    <HeadlineOfferContextProvider>
      <TestComponent />
    </HeadlineOfferContextProvider>,
    {
      storeOverrides: {
        offerer: MOCK_DATA.offerer,
      },
    }
  )
}

describe('HeadlineOfferContext', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.spyOn(api, 'getOffererHeadlineOffer').mockResolvedValue(
      MOCK_DATA.headlineOffer
    )
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({
          id: MOCK_DATA.headlineOffer.venueId,
          isVirtual: false,
          isPermanent: true,
        }),
      ],
    })
    localStorage.clear()
  })

  describe('should tell if headline offer is available as a feature', () => {
    it('should be available if feature is enabled and offerer is allowed to use it', async () => {
      renderIndividualOffersContext()

      await waitFor(async () => {
        const display = await screen.findByText(
          new RegExp(LABELS.display.isHeadlineOfferAllowedForOfferer)
        )
        expect(display.textContent).toContain('true')
      })
    })

    it('should not be available if offerer has only virtual venues', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue({
        venues: [
          makeVenueListItem({
            id: MOCK_DATA.headlineOffer.venueId,
            isVirtual: true,
            isPermanent: true,
          }),
        ],
      })

      renderIndividualOffersContext()

      await waitFor(async () => {
        const display = await screen.findByText(
          new RegExp(LABELS.display.isHeadlineOfferAllowedForOfferer)
        )
        expect(display.textContent).toContain('false')
      })
    })
  })

  it('should not be available if offerer has more than one non-virtual venue', async () => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({
          id: MOCK_DATA.headlineOffer.venueId,
          isVirtual: false,
          isPermanent: false,
        }),
        makeVenueListItem({
          id: MOCK_DATA.otherVenueOffer.venueId,
          isVirtual: false,
          isPermanent: true,
        }),
      ],
    })

    renderIndividualOffersContext()

    await waitFor(async () => {
      const display = await screen.findByText(
        new RegExp(LABELS.display.isHeadlineOfferAllowedForOfferer)
      )
      expect(display.textContent).toContain('false')
    })
  })

  it('should not be available if offerer has no permanent venue', async () => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({
          id: MOCK_DATA.headlineOffer.venueId,
          isVirtual: false,
          isPermanent: false,
        }),
      ],
    })

    renderIndividualOffersContext()

    await waitFor(async () => {
      const display = await screen.findByText(
        new RegExp(LABELS.display.isHeadlineOfferAllowedForOfferer)
      )
      expect(display.textContent).toContain('false')
    })
  })

  it('should fetch headline offer and make it available', async () => {
    renderIndividualOffersContext()

    await waitFor(async () => {
      const display = await screen.findByText(
        new RegExp(LABELS.display.headlineOffer)
      )
      expect(display.textContent).toContain(MOCK_DATA.headlineOffer.id)
    })
  })

  describe('upsertHeadlineOffer', () => {
    it('should upsert headline offer and update state', async () => {
      renderIndividualOffersContext()

      const upsertButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.upsertHeadlineOffer),
      })
      await userEvent.click(upsertButton)

      await waitFor(() => {
        expect(api.upsertHeadlineOffer).toHaveBeenCalledWith({
          offerId: MOCK_DATA.newHeadlineOffer.id,
        })
      })

      // We are not testing display update since this happens after a re-render,
      // which is triggered by the SWR mutate function on GET_OFFERER_HEADLINE_OFFER_QUERY_KEY.
      // This would be like testing the SWR library itself & its none of our concern.
      // Yet, we expect the mutation to be called.
      expect(mockMutate).toHaveBeenCalled()
    })

    describe('about notifications', () => {
      it('should notify success on successful upsert', async () => {
        const snackBarSuccess = vi.fn()
        vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
          success: snackBarSuccess,
          error: vi.fn(),
        }))

        renderIndividualOffersContext()

        const upsertButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.upsertHeadlineOffer),
        })
        await userEvent.click(upsertButton)

        expect(snackBarSuccess).toHaveBeenCalledWith(
          LABELS.notify.upsert.success
        )
      })

      it('should notify error on failed upsert', async () => {
        const snackBarError = vi.fn()
        vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
          success: vi.fn(),
          error: snackBarError,
        }))

        // Api call rejects with an error and so does the mutation.
        mockMutate.mockImplementation(() => Promise.reject())

        renderIndividualOffersContext()

        const upsertButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.upsertHeadlineOffer),
        })
        await userEvent.click(upsertButton)

        expect(snackBarError).toHaveBeenCalledWith(LABELS.notify.upsert.error)
      })
    })

    it('should log event on successful upsert', async () => {
      const logEvent = vi.fn()
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent,
      }))

      renderIndividualOffersContext()

      const upsertButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.upsertHeadlineOffer),
      })
      await userEvent.click(upsertButton)

      expect(logEvent).toHaveBeenCalledWith(
        Events.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER,
        {
          from: '/',
          actionType: 'add',
          requiredImageUpload: false,
        }
      )
    })
  })

  describe('removeHeadlineOffer', () => {
    it('should remove headline offer and update state', async () => {
      renderIndividualOffersContext()

      const removeButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.removeHeadlineOffer),
      })
      await userEvent.click(removeButton)

      // We are not testing display update since this happens after a re-render,
      // which is triggered by the SWR mutate function on GET_OFFERER_HEADLINE_OFFER_QUERY_KEY.
      // This would be like testing the SWR library itself & its none of our concern.
      // Yet, we expect the mutation to be called.
      expect(mockMutate).toHaveBeenCalled()
    })

    describe('about notifications', () => {
      it('should notify success on successful removal', async () => {
        const snackBarSuccess = vi.fn()
        vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
          success: snackBarSuccess,
          error: vi.fn(),
        }))

        renderIndividualOffersContext()

        const removeButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.removeHeadlineOffer),
        })
        await userEvent.click(removeButton)

        expect(snackBarSuccess).toHaveBeenCalledWith(
          LABELS.notify.delete.success
        )
      })

      it('should notify error on failed removal', async () => {
        const snackBarError = vi.fn()
        vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
          success: vi.fn(),
          error: snackBarError,
        }))

        // Api call rejects with an error and so does the mutation.
        mockMutate.mockImplementation(() => Promise.reject())

        renderIndividualOffersContext()

        const removeButton = await screen.findByRole('button', {
          name: new RegExp(LABELS.controls.removeHeadlineOffer),
        })
        await userEvent.click(removeButton)

        expect(snackBarError).toHaveBeenCalledWith(LABELS.notify.delete.error)
      })
    })

    it('should log event on successful removal', async () => {
      const logEvent = vi.fn()
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent,
      }))

      renderIndividualOffersContext()

      const removeButton = await screen.findByRole('button', {
        name: new RegExp(LABELS.controls.removeHeadlineOffer),
      })
      await userEvent.click(removeButton)

      expect(logEvent).toHaveBeenCalledWith(
        Events.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER,
        {
          from: '/',
          actionType: 'delete',
        }
      )
    })
  })
})
