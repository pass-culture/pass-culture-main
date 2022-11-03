import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { ApiError, GetIndividualOfferResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { FORM_DEFAULT_VALUES } from 'components/OfferIndividualForm'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { TOfferIndividualVenue } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'
import * as utils from 'screens/OfferIndividual/Informations/utils'
import { configureTestStore } from 'store/testUtils'

import { IInformationsProps, Informations as InformationsScreen } from '..'

jest.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: jest.fn(),
  }
})

window.matchMedia = jest.fn().mockReturnValue({ matches: true })

jest.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: jest.fn(),
}))

const renderInformationsScreen = (
  props: IInformationsProps,
  storeOverride: any,
  contextOverride: Partial<IOfferIndividualContext>
) => {
  const store = configureTestStore(storeOverride)
  const contextValue: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    ...contextOverride,
  }
  return render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={['/offre/AA/v3/creation/individuelle/informations']}
      >
        <Route path="/offre/AA/v3/creation/individuelle/informations">
          <OfferIndividualContext.Provider value={contextValue}>
            <InformationsScreen {...props} />
          </OfferIndividualContext.Provider>
        </Route>
        <Route path="/offre/AA/v3/creation/individuelle/stocks">
          <div>There is the stock route content</div>
        </Route>
      </MemoryRouter>
      <Notification />
    </Provider>
  )
}

const scrollIntoViewMock = jest.fn()

describe('screens:OfferIndividual::Informations::creation', () => {
  let props: IInformationsProps
  let store: any
  let contextOverride: Partial<IOfferIndividualContext>

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    store = {
      user: {
        initialized: true,
        currentUser: {
          publicName: 'John Do',
          isAdmin: false,
          email: 'email@example.com',
        },
      },
    }
    const categories = [
      {
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      },
    ]
    const subCategories = [
      {
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: true,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]

    const venue: TOfferIndividualVenue = {
      id: 'AA',
      name: 'Lieu offline AA',
      managingOffererId: 'A',
      isVirtual: false,
      withdrawalDetails: '',
      accessibility: {
        visual: false,
        mental: false,
        audio: false,
        motor: false,
        none: true,
      },
    }

    contextOverride = {
      venueList: [
        venue,
        {
          id: 'BB',
          name: 'Lieu online BB',
          managingOffererId: 'A',
          isVirtual: true,
          withdrawalDetails: '',
          accessibility: {
            visual: false,
            mental: false,
            audio: false,
            motor: false,
            none: true,
          },
        },
      ],
      offererNames: [{ id: 'A', name: 'mon offerer A' }],
      categories,
      subCategories,
    }

    props = {
      initialValues: FORM_DEFAULT_VALUES,
    }

    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
    jest.spyOn(api, 'postOffer').mockResolvedValue({ id: 'AA' })
    jest
      .spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
  })

  it('should submit minimal physical offer', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText("Titre de l'offre")
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(api.postOffer).toHaveBeenCalledWith({
      audioDisabilityCompliant: false,
      bookingEmail: null,
      description: null,
      durationMinutes: null,
      externalTicketOfficeUrl: null,
      extraData: {},
      isDuo: true,
      isEducational: false,
      isNational: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      name: 'Le nom de mon offre',
      offererId: 'A',
      subcategoryId: 'physical',
      url: null,
      venueId: 'AA',
      visualDisabilityCompliant: false,
      withdrawalDelay: null,
      withdrawalDetails: null,
      withdrawalType: null,
    })
    expect(api.getOffer).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
    expect(
      await screen.findByTestId('global-notification-success')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
  })

  it('should display api errors', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText("Titre de l'offre")
    await userEvent.type(nameField, 'Le nom de mon offre')

    jest.spyOn(api, 'postOffer').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: {
            name: 'api wrong name',
            venue: 'api wrong venue',
          },
        } as ApiResult,
        ''
      )
    )
    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(screen.getByText('api wrong name')).toBeInTheDocument()
    expect(screen.getByText('api wrong venue')).toBeInTheDocument()

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(api.getOffer).not.toHaveBeenCalled()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
  })

  it('should submit minimal virtual offer', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'virtual')
    const nameField = screen.getByLabelText("Titre de l'offre")
    await userEvent.type(nameField, 'Le nom de mon offre')

    const urlField = await screen.findByLabelText('URL d’accès à l’offre')

    await userEvent.type(urlField, 'http://example.com/')

    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(api.postOffer).toHaveBeenCalledWith({
      audioDisabilityCompliant: false,
      bookingEmail: null,
      description: null,
      durationMinutes: null,
      externalTicketOfficeUrl: null,
      extraData: {},
      isDuo: false,
      isEducational: false,
      isNational: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      name: 'Le nom de mon offre',
      offererId: 'A',
      subcategoryId: 'virtual',
      url: 'http://example.com/',
      venueId: 'BB',
      visualDisabilityCompliant: false,
      withdrawalDelay: null,
      withdrawalDetails: null,
      withdrawalType: null,
    })
    expect(api.getOffer).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByTestId('global-notification-success')
    ).toBeInTheDocument()
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
  })
})
