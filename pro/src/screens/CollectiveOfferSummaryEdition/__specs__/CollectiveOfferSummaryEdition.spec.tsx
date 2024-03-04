import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import { ApiError, CollectiveOfferResponseIdModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  Mode,
} from 'core/OfferEducational'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import {
  collectiveOfferTemplateFactory,
  defaultGetVenue,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSummaryEdition from '../CollectiveOfferSummaryEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const renderCollectiveOfferSummaryEdition = (
  offer: CollectiveOfferTemplate | CollectiveOffer
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        firstName: 'John',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        email: 'john@do.net',
        id: '1',
        isAdmin: false,
        isEmailValidated: true,
        roles: [],
      },
    },
  }

  renderWithProviders(
    <CollectiveOfferSummaryEdition
      offer={offer}
      reloadCollectiveOffer={vi.fn()}
      mode={Mode.EDITION}
    />,
    { storeOverrides }
  )
}

describe('CollectiveOfferSummary', () => {
  let offer: CollectiveOfferTemplate | CollectiveOffer
  const mockLogEvent = vi.fn()
  const notifyError = vi.fn()

  beforeEach(async () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true })

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.default>
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)

    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(offer)

    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [],
    })

    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'getNationalPrograms').mockResolvedValue([])

    vi.spyOn(api, 'createCollectiveOffer').mockResolvedValue(
      {} as CollectiveOfferResponseIdModel
    )
    fetchMock.mockIf(/image.jpg/, 'some response')
  })

  it('should display desactive offer option when offer is active and not booked', async () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })

    renderCollectiveOfferSummaryEdition(offer)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const desactivateOffer = screen.getByRole('button', {
      name: 'Masquer la publication sur Adage',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })

  it('should log event when clicking duplicate offer button', async () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    renderCollectiveOfferSummaryEdition(offer)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })
    await userEvent.click(duplicateOffer)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DUPLICATE_TEMPLATE_OFFER,
      {
        from: OFFER_FROM_TEMPLATE_ENTRIES.OFFER_TEMPLATE_RECAP,
      }
    )
  })

  it('should return an error when the collective offer could not be retrieved', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce('')

    renderCollectiveOfferSummaryEdition(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })
    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  })

  it('should return an error when the duplication failed', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(
      collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    )
    vi.spyOn(api, 'createCollectiveOffer').mockRejectedValueOnce(
      new ApiError({} as ApiRequestOptions, { status: 400 } as ApiResult, '')
    )

    renderCollectiveOfferSummaryEdition(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })

    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith(
      'Une ou plusieurs erreurs sont présentes dans le formulaire'
    )
  })

  it('should return an error when trying to get offerer image', async () => {
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    renderCollectiveOfferSummaryEdition(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })

    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith('Impossible de dupliquer l’image')
  })

  it('should return an error when trying to get offerer image blob', async () => {
    const mockResponse = new Response()
    vi.spyOn(mockResponse, 'blob').mockResolvedValue(
      Promise.resolve(undefined) as unknown as Blob
    )

    vi.spyOn(global, 'fetch').mockResolvedValue(mockResponse)

    renderCollectiveOfferSummaryEdition(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })

    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith('Impossible de dupliquer l’image')
  })
})
