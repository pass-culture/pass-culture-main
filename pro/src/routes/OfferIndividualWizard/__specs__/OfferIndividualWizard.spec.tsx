import '@testing-library/jest-dom'

import {
  render,
  screen,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ApiError } from 'apiClient/v2'
import { CATEGORY_STATUS } from 'core/Offers'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import Notification from 'new_components/Notification/Notification'
import { configureTestStore } from 'store/testUtils'

import { OfferIndividualWizard } from '..'

jest.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

const apiOffer: GetIndividualOfferResponseModel = {
  activeMediation: null,
  ageMax: null,
  ageMin: null,
  bookingEmail: null,
  conditions: null,
  dateCreated: '2022-05-18T08:25:30.991476Z',
  dateModifiedAtLastProvider: '2022-05-18T08:25:30.991481Z',
  description: 'A passionate description of product 80',
  durationMinutes: null,
  extraData: null,
  fieldsUpdated: [],
  hasBookingLimitDatetimesPassed: true,
  id: 'YA',
  isActive: true,
  isBookable: false,
  isDigital: false,
  isDuo: false,
  isEditable: true,
  isEducational: false,
  isEvent: true,
  isNational: false,
  isThing: false,
  audioDisabilityCompliant: false,
  mentalDisabilityCompliant: false,
  motorDisabilityCompliant: false,
  nonHumanizedId: 192,
  visualDisabilityCompliant: false,
  lastProvider: null,
  lastProviderId: null,
  mediaUrls: [],
  mediations: [],
  name: 'Séance ciné duo',
  product: {
    ageMax: null,
    ageMin: null,
    conditions: null,
    dateModifiedAtLastProvider: '2022-05-18T08:25:30.980975Z',
    description: 'A passionate description of product 80',
    durationMinutes: null,
    extraData: null,
    fieldsUpdated: [],
    id: 'AJFA',
    idAtProviders: null,
    isGcuCompatible: true,
    isNational: false,
    lastProviderId: null,
    mediaUrls: [],
    name: 'Product 80',
    owningOffererId: null,
    thumbCount: 0,
    url: null,
  },
  productId: 'AJFA',
  stocks: [
    {
      beginningDatetime: '2022-05-23T08:25:31.009799Z',
      bookingLimitDatetime: '2022-05-23T07:25:31.009799Z',
      bookingsQuantity: 2,
      cancellationLimitDate: '2022-06-01T12:15:12.343431Z',
      dateCreated: '2022-05-18T08:25:31.015652Z',
      dateModified: '2022-05-18T08:25:31.015655Z',
      dateModifiedAtLastProvider: '2022-05-18T08:25:31.015643Z',
      fieldsUpdated: [],
      hasActivationCode: false,
      id: 'YE',
      idAtProviders: null,
      isBookable: false,
      isEventDeletable: false,
      isEventExpired: true,
      isSoftDeleted: false,
      lastProviderId: null,
      offerId: 'YA',
      price: 10,
      quantity: 1000,
      remainingQuantity: 998,
    },
  ],
  subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
  thumbUrl: null,
  externalTicketOfficeUrl: null,
  url: null,
  venue: {
    address: '1 boulevard Poissonnière',
    bookingEmail: 'venue29@example.net',
    city: 'Paris',
    comment: null,
    dateCreated: '2022-05-18T08:25:30.929961Z',
    dateModifiedAtLastProvider: '2022-05-18T08:25:30.929955Z',
    departementCode: '75',
    fieldsUpdated: [],
    id: 'DY',
    idAtProviders: null,
    isVirtual: false,
    lastProviderId: null,
    latitude: 48.87004,
    longitude: 2.3785,
    managingOfferer: {
      address: '1 boulevard Poissonnière',
      city: 'Paris',
      dateCreated: '2022-05-18T08:25:30.891369Z',
      dateModifiedAtLastProvider: '2022-05-18T08:25:30.891364Z',
      fieldsUpdated: [],
      id: 'CU',
      idAtProviders: null,
      isActive: true,
      isValidated: true,
      lastProviderId: null,
      name: 'Le Petit Rintintin Management 6',
      postalCode: '75000',
      siren: '000000006',
      thumbCount: 0,
    },
    managingOffererId: 'CU',
    name: 'Cinéma synchro avec booking provider',
    postalCode: '75000',
    publicName: 'Cinéma synchro avec booking provider',
    siret: '00000000600029',
    thumbCount: 0,
    venueLabelId: null,
    audioDisabilityCompliant: false,
    mentalDisabilityCompliant: false,
    motorDisabilityCompliant: false,
    visualDisabilityCompliant: false,
  },
  venueId: 'DY',
  withdrawalDetails: null,
  status: OfferStatus.EXPIRED,
  withdrawalType: null,
  withdrawalDelay: null,
}

const renderOfferIndividualWizardRoute = (
  storeOverride: any,
  url = '/offre/v3'
) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Route path={['/offre/v3', '/offre/:offerId/v3']}>
          <OfferIndividualWizard />
        </Route>
        <Route path={['/structures', '/accueil']}>Home Page</Route>
      </MemoryRouter>
      <Notification />
    </Provider>
  )
}
describe('test OfferIndividualWisard', () => {
  let store: any

  beforeEach(() => {
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
    jest
      .spyOn(api, 'listOfferersNames')
      .mockResolvedValue({ offerersNames: [] })
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({ categories: [], subcategories: [] })
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  })

  it('should display an error when unable to load offer', async () => {
    jest.spyOn(api, 'getOffer').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            global: ['Une erreur est survenue'],
          },
        } as ApiResult,
        ''
      )
    )
    renderOfferIndividualWizardRoute(store, '/offre/OFFER_ID/v3/creation')
    await waitForElementToBeRemoved(() =>
      screen.getByText(/Chargement en cours/)
    )
    expect(
      await screen.findByText(
        /Une erreur est survenue lors de la récupération de votre offre/
      )
    ).toBeInTheDocument()
  })
  it('should display an error when unable to load categories', async () => {
    jest.spyOn(api, 'getCategories').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            global: ['Une erreur est survenue'],
          },
        } as ApiResult,
        ''
      )
    )
    renderOfferIndividualWizardRoute(
      store,
      '/offre/v3/creation/individuelle/informations/'
    )
    await waitForElementToBeRemoved(() =>
      screen.getByText(/Chargement en cours/)
    )
    expect(screen.getByText(GET_DATA_ERROR_MESSAGE)).toBeInTheDocument()
  })

  it('should initialize context with api', async () => {
    renderOfferIndividualWizardRoute(
      store,
      '/offre/v3/creation/individuelle/informations'
    )
    expect(
      await screen.findByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      undefined // offererId
    )
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validatedForUser
      null, // validated
      true, // activeOfferersOnly,
      undefined // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should initialize context with api when offererId is given in query', async () => {
    renderOfferIndividualWizardRoute(
      store,
      '/offre/v3/creation/individuelle/informations/?structure=CU'
    )
    expect(
      await screen.findByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      undefined // offererId
    )
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validatedForUser
      null, // validated
      true, // activeOfferersOnly,
      'CU' // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should initialize context with api when a offerId is given', async () => {
    jest.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [
        {
          id: 'A',
          proLabel: 'Category name',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: SubcategoryIdEnum.SEANCE_CINE,
          proLabel: 'Sub category name',
          appLabel: 'Sub category name',
          categoryId: 'A',
          isSelectable: true,
          canBeDuo: true,
          canBeEducational: true,
          canExpire: false,
          conditionalFields: [],
          isDigitalDeposit: false,
          isEvent: true,
          isPhysicalDeposit: true,
          onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
          reimbursementRule: '',
        },
      ],
    })
    const offerId = 'YA'
    renderOfferIndividualWizardRoute(
      store,
      `/offre/${offerId}/v3/individuelle/informations?structure=CU`
    )
    expect(
      await screen.findByRole('heading', { name: "Modifier l'offre" })
    ).toBeInTheDocument()
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      undefined // offererId
    )
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validatedForUser
      null, // validated
      true, // activeOfferersOnly,
      apiOffer.venue.managingOfferer.id // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).toHaveBeenCalledWith(offerId)
  })

  describe('stepper', () => {
    it('should not render stepper on information page', async () => {
      renderOfferIndividualWizardRoute(
        store,
        `/offre/v3/creation/individuelle/informations`
      )

      expect(
        await screen.findByRole('heading', { name: 'Créer une offre' })
      ).toBeInTheDocument()

      const tabInformations = screen.getByText('Informations', {
        selector: 'span',
      })
      const tabStocks = screen.getByText('Stock & Prix', {
        selector: 'span',
      })
      const tabSummary = screen.getByText('Récapitulatif', {
        selector: 'span',
      })
      const tabConfirmation = screen.getByText('Confirmation', {
        selector: 'span',
      })

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
    })

    it('should not render stepper on confirmation page', async () => {
      const offerId = 'YA'
      renderOfferIndividualWizardRoute(
        store,
        `/offre/${offerId}/v3/individuelle/confirmation`
      )

      expect(
        await screen.findByRole('heading', { name: 'Confirmation' })
      ).toBeInTheDocument()

      const tabInformations = screen.queryByText('Informations', {
        selector: 'span',
      })
      const tabStocks = screen.queryByText('Stock & Prix', {
        selector: 'span',
      })
      const tabSummary = screen.queryByText('Récapitulatif', {
        selector: 'span',
      })
      const tabConfirmation = screen.queryByText('Confirmation', {
        selector: 'span',
      })

      expect(tabInformations).not.toBeInTheDocument()
      expect(tabStocks).not.toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()
    })

    it('should render stepper on summary page in creation', async () => {
      renderOfferIndividualWizardRoute(
        store,
        `/offre/creation/v3/individuelle/recapitulatif`
      )
      expect(
        await screen.findByRole('heading', { name: 'Récapitulatif' })
      ).toBeInTheDocument()

      const tabInformations = screen.getByText('Informations', {
        selector: 'span',
      })
      const tabStocks = screen.getByText('Stock & Prix', {
        selector: 'span',
      })
      const tabSummary = screen.getByText('Récapitulatif', {
        selector: 'span',
      })
      const tabConfirmation = screen.getByText('Confirmation', {
        selector: 'span',
      })
      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
    })

    it('should not render stepper on summary page in edition', async () => {
      const offerId = 'YA'
      renderOfferIndividualWizardRoute(
        store,
        `/offre/${offerId}/v3/individuelle/recapitulatif`
      )
      expect(
        await screen.findByRole('heading', { name: 'Récapitulatif' })
      ).toBeInTheDocument()

      const tabInformations = screen.queryByText('Informations', {
        selector: 'span',
      })
      const tabStocks = screen.queryByText('Stock & Prix', {
        selector: 'span',
      })
      const tabSummary = screen.queryByText('Récapitulatif', {
        selector: 'span',
      })
      const tabConfirmation = screen.queryByText('Confirmation', {
        selector: 'span',
      })

      expect(tabInformations).not.toBeInTheDocument()
      expect(tabStocks).not.toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()
    })
  })
})
