import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import router from 'react-router-dom'

import { api } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { collectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferFromRequest from '../CollectiveOfferFromRequest'

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

describe('CollectiveOfferCreation', () => {
  const notifyError = jest.fn()

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
      email: 'request@example.com',
    })

    renderWithProviders(<CollectiveOfferFromRequest />)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getCollectiveOfferTemplate).toHaveBeenCalledTimes(1)
    expect(api.getCollectiveOfferRequest).toHaveBeenCalledTimes(1)

    expect(screen.getByText('request@example.com')).toBeInTheDocument()
    expect(screen.getByText('Test unit')).toBeInTheDocument()
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
})
