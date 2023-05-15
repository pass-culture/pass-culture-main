import { screen } from '@testing-library/react'
import React from 'react'
import router from 'react-router-dom'

import { api } from 'apiClient/api'
import * as createFromTemplateUtils from 'core/OfferEducational/utils/createOfferFromTemplate'
import { collectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferFromRequest from '../CollectiveOfferFromRequest'

jest.mock('apiClient/api', () => ({
  api: {
    getCategories: jest.fn(),
    listEducationalDomains: jest.fn(),
    listEducationalOfferers: jest.fn(),
    canOffererCreateEducationalOffer: jest.fn(),
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

const mockedUsedNavigate = jest.fn()

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offerId: jest.fn(),
  }),
  useNavigate: () => mockedUsedNavigate,
}))

describe('CollectiveOfferCreation', () => {
  it('should create new offer from template when id params exist ', async () => {
    const offerTemplate = collectiveOfferTemplateFactory({
      educationalPriceDetail: 'Details from template',
    })
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: '1' })
    jest
      .spyOn(api, 'getCollectiveOfferTemplate')
      .mockResolvedValue(offerTemplate)
    jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    renderWithProviders(<CollectiveOfferFromRequest />)

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
    expect(
      createFromTemplateUtils.createOfferFromTemplate
    ).toHaveBeenCalledTimes(1)
  })

  it('should display spinner when id params doesnt exist', async () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: '' })
    renderWithProviders(<CollectiveOfferFromRequest />)

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
    expect(mockedUsedNavigate).toHaveBeenCalledWith('/accueil')
  })

  it('should redirect to accueil when id params rejected', async () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: '123' })

    jest.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce('')
    renderWithProviders(<CollectiveOfferFromRequest />)

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
    expect(mockedUsedNavigate).toHaveBeenCalledWith('/accueil')
  })
})
