import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { Events } from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual, IOfferSubCategory } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { AccessiblityEnum } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import * as useAnalytics from 'hooks/useAnalytics'
import * as pcapi from 'repository/pcapi/pcapi'
import * as utils from 'screens/OfferIndividual/Informations/utils'
import { renderWithProviders } from 'utils/renderWithProviders'

import { IInformationsProps, Informations as InformationsScreen } from '..'

window.matchMedia = jest.fn().mockReturnValue({ matches: true })
const mockLogEvent = jest.fn()

jest.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: jest.fn(),
  }
})
jest.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: jest.fn(),
}))
const scrollIntoViewMock = jest.fn()

const renderInformationsScreen = (
  props: IInformationsProps,
  contextOverride: Partial<IOfferIndividualContext>
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }
  const contextValue: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }
  return renderWithProviders(
    <>
      <Routes>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
          element={
            <OfferIndividualContext.Provider value={contextValue}>
              <InformationsScreen {...props} />
            </OfferIndividualContext.Provider>
          }
        />
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
          element={<div>There is the stock route content</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
      ],
    }
  )
}

describe('screens:OfferIndividual::Informations:draft', () => {
  let props: IInformationsProps
  let contextOverride: Partial<IOfferIndividualContext>
  let offer: IOfferIndividual
  let subCategories: IOfferSubCategory[]
  const offererId = 1
  const physicalVenueId = 1
  const virtualVenueId = 1
  const offerId = 12

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]

    const venue: TOfferIndividualVenue = {
      id: 'AE',
      nonHumanizedId: physicalVenueId,
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
      hasMissingReimbursementPoint: false,
      hasCreatedOffer: true,
    }

    offer = {
      nonHumanizedId: offerId,
      author: 'Offer author',
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      isbn: '',
      isActive: true,
      isDuo: false,
      isEvent: false,
      isDigital: false,
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
      offererId: 12,
      offererName: '',
      performer: 'Offer performer',
      ean: '',
      showSubType: '',
      showType: '',
      stageDirector: 'Offer stageDirector',
      speaker: 'Offer speaker',
      subcategoryId: 'SCID physical',
      image: undefined,
      url: 'http://offer.example.com',
      externalTicketOfficeUrl: 'http://external.example.com',
      venueId: 2,
      venue: {
        id: 2,
        name: 'Venue name',
        publicName: 'Venue publicName',
        isVirtual: false,
        address: '15 rue de la corniche',
        postalCode: '75001',
        city: 'Paris',
        offerer: {
          nonHumanizedId: 1,
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
      status: OfferStatus.DRAFT,
    }

    contextOverride = {
      offerId: offer.nonHumanizedId,
      offer: offer,
      venueList: [
        venue,
        {
          id: 'A9',
          nonHumanizedId: 2,
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
          hasMissingReimbursementPoint: false,
          hasCreatedOffer: true,
        },
      ],
      offererNames: [{ nonHumanizedId: 1, name: 'Offerer name' }],
      categories,
      subCategories,
    }

    props = {
      offererId: offererId.toString(),
      venueId: physicalVenueId.toString(),
    }

    jest
      .spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
    jest.spyOn(api, 'patchOffer').mockResolvedValue({
      nonHumanizedId: offerId,
    } as GetIndividualOfferResponseModel)
    jest.spyOn(api, 'postOffer').mockResolvedValue({
      nonHumanizedId: offerId,
    } as GetIndividualOfferResponseModel)
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
    jest.spyOn(api, 'deleteThumbnail').mockResolvedValue()
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should submit minimal physical offer', async () => {
    renderInformationsScreen(props, contextOverride)
    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(api.patchOffer).toHaveBeenCalledTimes(1)
    expect(api.getOffer).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByTestId('global-notification-success')
    ).toBeInTheDocument()
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })

  it('should submit minimal virtual offer', async () => {
    contextOverride.offer = {
      ...offer,
      venueId: virtualVenueId,
      subcategoryId: 'SCID virtual',
      isEvent: false,
      withdrawalDelay: null,
      withdrawalType: null,
    }
    props = {
      offererId: offererId.toString(),
      venueId: virtualVenueId.toString(),
    }

    renderInformationsScreen(props, contextOverride)
    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(api.patchOffer).toHaveBeenCalledTimes(1)
    expect(api.getOffer).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByTestId('global-notification-success')
    ).toBeInTheDocument()
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })

  it('should track when creating draft offer using Étape suivante', async () => {
    renderInformationsScreen(props, contextOverride)
    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: true,
        isEdition: true,
        offerId: offerId,
        to: 'stocks',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when creating draft offer using Sauvegarder le brouillon', async () => {
    renderInformationsScreen(props, contextOverride)
    await userEvent.click(await screen.findByText('Sauvegarder le brouillon'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: true,
        isEdition: true,
        offerId: offerId,
        to: 'informations',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when cancelling draft edition', async () => {
    renderInformationsScreen(props, contextOverride)

    await userEvent.click(await screen.findByText('Annuler et quitter'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: true,
        isEdition: true,
        offerId: offerId,
        to: 'Offers',
        used: 'StickyButtons',
      }
    )
  })
})
