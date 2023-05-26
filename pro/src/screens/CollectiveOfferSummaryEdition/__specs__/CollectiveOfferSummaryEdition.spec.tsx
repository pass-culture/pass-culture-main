import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import React from 'react'

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
  EducationalCategories,
  Mode,
} from 'core/OfferEducational'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import {
  categoriesFactory,
  subCategoriesFactory,
} from 'screens/OfferEducational/__tests-utils__'
import {
  collectiveOfferTemplateFactory,
  defaultVenueResponseModel,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSummaryEdition from '../CollectiveOfferSummaryEdition'

const renderCollectiveOfferSummaryEdition = (
  offer: CollectiveOfferTemplate | CollectiveOffer,
  categories: EducationalCategories
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        firstName: 'John',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        email: 'john@do.net',
        id: '1',
        nonHumanizedId: '1',
        isAdmin: false,
        isEmailValidated: true,
        roles: [],
      },
    },
  }

  renderWithProviders(
    <CollectiveOfferSummaryEdition
      offer={offer}
      categories={categories}
      reloadCollectiveOffer={jest.fn()}
      mode={Mode.EDITION}
    />,
    { storeOverrides }
  )
}

describe('CollectiveOfferSummary', () => {
  let offer: CollectiveOfferTemplate | CollectiveOffer
  let categories: EducationalCategories
  const mockLogEvent = jest.fn()
  const notifyError = jest.fn()

  beforeEach(() => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true })
    categories = {
      educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
      educationalSubCategories: subCategoriesFactory([
        { categoryId: 'CAT_1', id: 'SUBCAT_1' },
      ]),
    }

    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      error: notifyError,
    }))

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))

    jest.spyOn(api, 'getVenue').mockResolvedValue(defaultVenueResponseModel)

    jest.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(offer)

    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({ categories: [], subcategories: [] })

    jest
      .spyOn(api, 'listEducationalOfferers')
      .mockResolvedValue({ educationalOfferers: [] })

    jest.spyOn(api, 'listEducationalDomains').mockResolvedValue([])

    jest
      .spyOn(api, 'createCollectiveOffer')
      .mockResolvedValue({} as CollectiveOfferResponseIdModel)
    fetchMock.mockIf(/image.jpg/, 'some response')
  })

  it('should display desactive offer option when offer is active and not booked', async () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })

    renderCollectiveOfferSummaryEdition(offer, categories)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const desactivateOffer = screen.getByRole('button', {
      name: 'Masquer la publication sur Adage',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })

  it('should log event when clicking duplicate offer button', async () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    renderCollectiveOfferSummaryEdition(offer, categories)
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
    jest.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce('')

    renderCollectiveOfferSummaryEdition(offer, categories)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })
    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  })

  it('should return an error when the categorie call failed', async () => {
    jest.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(offer)

    jest.spyOn(api, 'getCategories').mockRejectedValueOnce('')

    renderCollectiveOfferSummaryEdition(offer, categories)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })
    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
  })

  it('should return an error when the duplication failed', async () => {
    jest.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(offer)
    jest
      .spyOn(api, 'createCollectiveOffer')
      .mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 400 } as ApiResult, '')
      )

    renderCollectiveOfferSummaryEdition(offer, categories)

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

    renderCollectiveOfferSummaryEdition(offer, categories)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })

    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith("Impossible de dupliquer l'image")
  })

  it('should return an error when trying to get offerer image blob', async () => {
    const mockResponse = new Response()
    jest
      .spyOn(mockResponse, 'blob')
      .mockResolvedValue(Promise.resolve(undefined) as unknown as Blob)

    jest.spyOn(global, 'fetch').mockResolvedValue(mockResponse)

    renderCollectiveOfferSummaryEdition(offer, categories)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })

    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith("Impossible de dupliquer l'image")
  })
})
