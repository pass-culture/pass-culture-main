import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import router from 'react-router-dom'

import { api } from 'apiClient/api'
import * as createFromTemplateUtils from 'core/OfferEducational/utils/createOfferFromTemplate'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import { collectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferFromRequest from '../CollectiveOfferFromRequest'

const mockLogEvent = jest.fn()

jest.mock('apiClient/api', () => ({
  api: {
    getCollectiveOfferTemplate: jest.fn(),
    getCollectiveOfferRequest: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offerId: jest.fn(),
    requestId: jest.fn(),
  }),
}))

jest.mock('core/OfferEducational/utils/createOfferFromTemplate', () => ({
  createOfferFromTemplate: jest.fn(),
}))

describe('CollectiveOfferCreation', () => {
  const notifyError = jest.fn()
  const institution = {
    city: 'Paris',
    institutionId: '123456',
    institutionType: 'LYCEE POLYVALENT',
    name: 'test request clg',
    postalCode: '75000',
  }

  beforeEach(() => {
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      error: notifyError,
    }))
  })
  it('should display request information', async () => {
    const offerTemplate = collectiveOfferTemplateFactory()
    jest
      .spyOn(router, 'useParams')
      .mockReturnValue({ offerId: '1', requestId: '2' })
    jest
      .spyOn(api, 'getCollectiveOfferTemplate')
      .mockResolvedValueOnce(offerTemplate)
    jest.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce({
      comment: 'Test unit',
      redactor: {
        email: 'request@example.com',
        firstName: 'Reda',
        lastName: 'Khteur',
      },
      institution,
      dateCreated: '2030-06-20',
      requestedDate: '2030-06-27',
    })

    renderWithProviders(<CollectiveOfferFromRequest />)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getCollectiveOfferTemplate).toHaveBeenCalledTimes(1)
    expect(api.getCollectiveOfferRequest).toHaveBeenCalledTimes(1)

    expect(screen.getByText('request@example.com')).toBeInTheDocument()
    expect(screen.getByText('Test unit')).toBeInTheDocument()
    expect(screen.getByText('Offre de test')).toBeInTheDocument()
    expect(screen.getByText('20 juin 2030')).toBeInTheDocument()
    expect(
      screen.getByText(/LYCEE POLYVALENT test request clg/)
    ).toBeInTheDocument()
    expect(screen.getByText(/75000 Paris/)).toBeInTheDocument()
    expect(screen.getByText('27 juin 2030')).toBeInTheDocument()
  })

  it('should display spinner when id params doesnt exist', async () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: '' })
    renderWithProviders(<CollectiveOfferFromRequest />)

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should call api and get error', async () => {
    jest
      .spyOn(router, 'useParams')
      .mockReturnValue({ offerId: '1', requestId: '2' })
    jest.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce({
      isOk: false,
      message: 'Une erreur est survenue lors de la récupération de votre offre',
      payload: null,
    })
    jest.spyOn(api, 'getCollectiveOfferRequest').mockRejectedValueOnce({
      isOk: false,
      message: 'Une erreur est survenue lors de la récupération de votre offre',
      payload: null,
    })

    renderWithProviders(<CollectiveOfferFromRequest />)

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()

    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'Une erreur est survenue lors de la récupération de votre offre'
    )
    expect(notifyError).toHaveBeenNthCalledWith(
      2,
      'Nous avons rencontré un problème lors de la récupération des données.'
    )
  })

  it('should create offer on button click', async () => {
    const offerTemplate = collectiveOfferTemplateFactory()

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    jest
      .spyOn(router, 'useParams')
      .mockReturnValue({ offerId: '1', requestId: '2' })
    jest
      .spyOn(api, 'getCollectiveOfferTemplate')
      .mockResolvedValueOnce(offerTemplate)
    jest.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce({
      comment: 'Test unit',
      redactor: { email: 'request@example.com' },
      institution,
    })
    jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    renderWithProviders(<CollectiveOfferFromRequest />)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const requestButton = screen.getByText('Créer l’offre pour l’enseignant')

    await userEvent.click(requestButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
  })
})
