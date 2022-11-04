import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers'
import { configureTestStore } from 'store/testUtils'

import { OfferIndividualWizard } from '..'

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
      </MemoryRouter>
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
          isAdmin: true,
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

  it('should initialize context with api with offererId on query', async () => {
    await renderOfferIndividualWizardRoute(
      store,
      '/offre/v3/creation/individuelle/informations?structure=CU'
    )
    expect(
      await screen.findByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(await screen.findByLabelText('Catégorie')).toBeInTheDocument()
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validatedForUser,
      null, // validated,
      true, // activeOfferersOnly,
      'CU' // offererId
    )
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      'CU' // offererId
    )

    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should display admin creation banner when no offererId is given', async () => {
    await renderOfferIndividualWizardRoute(
      store,
      '/offre/v3/creation/individuelle/informations'
    )
    expect(
      await screen.findByText(
        'Afin de créer une offre en tant qu’administrateur veuillez sélectionner une structure.'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Type d’offre' })
    ).not.toBeInTheDocument()

    expect(api.getVenues).not.toHaveBeenCalled()
    expect(api.listOfferersNames).not.toHaveBeenCalled()
    expect(api.getCategories).not.toHaveBeenCalled()
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
    await renderOfferIndividualWizardRoute(
      store,
      `/offre/${offerId}/v3/individuelle/informations?structure=CU`
    )
    expect(
      await screen.findByRole('heading', { name: "Modifier l'offre" })
    ).toBeInTheDocument()
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validatedForUser
      null, // validated
      true, // activeOfferersOnly,
      apiOffer.venue.managingOfferer.id // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()

    expect(api.listOfferersNames).not.toHaveBeenCalled()
    expect(api.getOffer).toHaveBeenCalledWith(offerId)
  })
})
