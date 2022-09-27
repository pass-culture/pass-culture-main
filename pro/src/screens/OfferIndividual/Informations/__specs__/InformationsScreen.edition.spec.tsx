import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { WithdrawalTypeEnum } from 'apiClient/v1'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS, OFFER_STATUS_ACTIVE } from 'core/Offers'
import { IOfferIndividual, IOfferSubCategory } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { setInitialFormValues } from 'new_components/OfferIndividualForm'
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

jest.mock('apiClient/api', () => ({
  api: {
    postOffer: jest.fn(),
    patchOffer: jest.fn(),
  },
}))
jest.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: jest.fn(),
}))

const renderInformationsScreen = (
  props: IInformationsProps,
  storeOverride: any,
  contextValue: IOfferIndividualContext
) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <OfferIndividualContext.Provider value={contextValue}>
          <InformationsScreen {...props} />
        </OfferIndividualContext.Provider>
      </MemoryRouter>
    </Provider>
  )
}

const scrollIntoViewMock = jest.fn()

describe('screens:OfferIndividual::Informations:edition', () => {
  let props: IInformationsProps
  let store: any
  let contextValue: IOfferIndividualContext
  let offer: IOfferIndividual
  let subCategories: IOfferSubCategory[]

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
        id: 'CID',
        proLabel: 'Catégorie CID',
        isSelectable: true,
      },
    ]
    subCategories = [
      {
        id: 'SCID virtual',
        categoryId: 'CID',
        proLabel: 'Sous catégorie online de CID',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'SCID physical',
        categoryId: 'CID',
        proLabel: 'Sous catégorie offline de CID',
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
      id: 'VID physical',
      name: 'Venue name',
      isVirtual: false,
      accessibility: {
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.NONE]: true,
      },
      managingOffererId: 'OFID',
      withdrawalDetails: '',
    }

    offer = {
      id: 'AA',
      nonHumanizedId: 12,
      author: 'Offer author',
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      isbn: '',
      isDuo: false,
      isEducational: false,
      isEvent: true,
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
      isNational: false,
      name: 'Offer name',
      musicSubType: '',
      musicType: '',
      offererId: 'OFID',
      offererName: '',
      performer: 'Offer performer',
      showSubType: '',
      showType: '',
      stageDirector: 'Offer stageDirector',
      speaker: 'Offer speaker',
      subcategoryId: 'SCID physical',
      image: undefined,
      url: 'http://offer.example.com',
      externalTicketOfficeUrl: 'http://external.example.com',
      venueId: 'VID physical',
      venue: {
        id: 'VID physical',
        name: 'Venue name',
        publicName: 'Venue publicName',
        isVirtual: false,
        address: '15 rue de la corniche',
        postalCode: '75001',
        city: 'Paris',
        offerer: {
          id: 'OFID',
          name: 'Offerer name',
        },
        departmentCode: '75',
        accessibility: {
          [AccessiblityEnum.AUDIO]: false,
          [AccessiblityEnum.MENTAL]: false,
          [AccessiblityEnum.MOTOR]: false,
          [AccessiblityEnum.VISUAL]: false,
          [AccessiblityEnum.NONE]: true,
        },
      },
      visa: '',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      stocks: [],
      lastProviderName: null,
      lastProvider: null,
      status: OFFER_STATUS_ACTIVE,
    }

    contextValue = {
      offerId: offer.id,
      offer: offer,
      venueList: [
        venue,
        {
          id: 'VID virtual',
          name: 'Lieu online BB',
          managingOffererId: 'OFID',
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
      offererNames: [{ id: 'OFID', name: 'Offerer name' }],
      categories,
      subCategories,
      reloadOffer: () => {},
    }

    props = {
      initialValues: setInitialFormValues(offer, subCategories),
    }

    jest
      .spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
  })

  it('should submit minimal physical offer', async () => {
    renderInformationsScreen(props, store, contextValue)
    const nameField = screen.getByLabelText("Titre de l'offre")
    await userEvent.clear(nameField)
    await userEvent.type(nameField, 'Le nom de mon offre édité')

    await userEvent.click(await screen.findByText('Suivant'))

    await waitFor(() => {
      expect(api.patchOffer).toHaveBeenCalledTimes(1)
      expect(api.patchOffer).toHaveBeenCalledWith('AA', {
        audioDisabilityCompliant: true,
        bookingEmail: 'booking@email.com',
        description: 'Offer description',
        durationMinutes: 140,
        externalTicketOfficeUrl: 'http://external.example.com',
        extraData: {
          author: 'Offer author',
          isbn: '',
          musicSubType: '',
          musicType: '',
          performer: 'Offer performer',
          showSubType: '',
          showType: '',
          speaker: 'Offer speaker',
          stageDirector: 'Offer stageDirector',
          visa: '',
        },
        isDuo: false,
        isNational: false,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        name: 'Le nom de mon offre édité',
        venueId: 'VID physical',
        visualDisabilityCompliant: true,
        withdrawalDetails: 'Offer withdrawalDetails',
        withdrawalDelay: 140,
        withdrawalType: WithdrawalTypeEnum.ON_SITE,
      })
    })
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })

  it('should submit minimal virtual offer', async () => {
    contextValue.offer = {
      ...offer,
      venueId: 'VID virtual',
      subcategoryId: 'SCID virtual',
      isEvent: false,
      withdrawalDelay: null,
      withdrawalType: null,
    }
    props = {
      initialValues: setInitialFormValues(contextValue.offer, subCategories),
    }

    renderInformationsScreen(props, store, contextValue)
    const nameField = screen.getByLabelText("Titre de l'offre")
    await userEvent.clear(nameField)
    await userEvent.type(nameField, 'Le nom de mon offre édité')

    await userEvent.click(await screen.findByText('Suivant'))

    await waitFor(() => {
      expect(api.patchOffer).toHaveBeenCalledTimes(1)
      expect(api.patchOffer).toHaveBeenCalledWith('AA', {
        audioDisabilityCompliant: true,
        bookingEmail: 'booking@email.com',
        description: 'Offer description',
        durationMinutes: 140,
        externalTicketOfficeUrl: 'http://external.example.com',
        extraData: {
          author: 'Offer author',
          isbn: '',
          musicSubType: '',
          musicType: '',
          performer: 'Offer performer',
          showSubType: '',
          showType: '',
          speaker: 'Offer speaker',
          stageDirector: 'Offer stageDirector',
          visa: '',
        },
        isDuo: false,
        isNational: false,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        name: 'Le nom de mon offre édité',
        venueId: 'VID virtual',
        visualDisabilityCompliant: true,
        withdrawalDetails: 'Offer withdrawalDetails',
        withdrawalDelay: undefined,
        withdrawalType: undefined,
      })
    })
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })
})
