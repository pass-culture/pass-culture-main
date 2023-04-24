import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError, GetIndividualOfferResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { Events } from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { TOfferIndividualVenue } from 'core/Venue/types'
import * as useAnalytics from 'hooks/useAnalytics'
import * as pcapi from 'repository/pcapi/pcapi'
import * as utils from 'screens/OfferIndividual/Informations/utils'
import { renderWithProviders } from 'utils/renderWithProviders'

import { IInformationsProps, Informations as InformationsScreen } from '..'

const mockLogEvent = jest.fn()

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
            mode: OFFER_WIZARD_MODE.CREATION,
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
            mode: OFFER_WIZARD_MODE.CREATION,
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
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
      ],
    }
  )
}

const scrollIntoViewMock = jest.fn()

describe('screens:OfferIndividual::Informations::creation', () => {
  let props: IInformationsProps
  let contextOverride: Partial<IOfferIndividualContext>
  const offererId = 1
  const offerId = 5

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const categories = [
      {
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      },
    ]
    const subCategories: IOfferSubCategory[] = [
      {
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
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
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
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
      nonHumanizedId: 1,
      name: 'Lieu offline AA',
      managingOffererId: 'AE',
      isVirtual: false,
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
    }

    contextOverride = {
      venueList: [
        venue,
        {
          id: 'A9',
          nonHumanizedId: 2,
          name: 'Lieu online BB',
          managingOffererId: 'AE',
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
      offererNames: [{ nonHumanizedId: offererId, name: 'mon offerer A' }],
      categories,
      subCategories,
    }

    props = {
      offererId: offererId.toString(),
      venueId: venue.nonHumanizedId.toString(),
    }

    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
    jest.spyOn(api, 'postOffer').mockResolvedValue({
      nonHumanizedId: offerId,
    } as GetIndividualOfferResponseModel)
    jest
      .spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should submit minimal physical offer', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
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
      isNational: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      name: 'Le nom de mon offre',
      subcategoryId: 'physical',
      url: null,
      venueId: 1,
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
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
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
    const nextButton = screen.getByText('Étape suivante')
    const draftButton = screen.getByText('Sauvegarder le brouillon')

    await userEvent.click(screen.getByText('Étape suivante'))

    await waitFor(() => {
      expect(api.postOffer).toHaveBeenCalledTimes(1)
      expect(api.getOffer).not.toHaveBeenCalled()
    })

    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(await screen.findByText('api wrong name')).toBeInTheDocument()
    expect(screen.getByText('api wrong venue')).toBeInTheDocument()
    expect(nextButton).not.toBeDisabled()
    expect(draftButton).not.toBeDisabled()
  })

  it('should submit minimal virtual offer', async () => {
    // Use virtual venue
    props.venueId = '2'
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'virtual')

    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    const urlField = await screen.findByLabelText('URL d’accès à l’offre')

    await userEvent.type(urlField, 'https://example.com/')

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
      isNational: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      name: 'Le nom de mon offre',
      subcategoryId: 'virtual',
      url: 'https://example.com/',
      venueId: 2,
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
  it('should leave the user to creation page on draft save', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(await screen.findByText('Sauvegarder le brouillon'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(api.postOffer).toHaveBeenCalledWith({
      audioDisabilityCompliant: false,
      bookingEmail: null,
      description: null,
      durationMinutes: null,
      externalTicketOfficeUrl: null,
      extraData: {},
      isDuo: true,
      isNational: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      name: 'Le nom de mon offre',
      subcategoryId: 'physical',
      url: null,
      venueId: 1,
      visualDisabilityCompliant: false,
      withdrawalDelay: null,
      withdrawalDetails: null,
      withdrawalType: null,
    })
    expect(
      screen.getByText(
        'Tous les champs sont obligatoires sauf mention contraire.'
      )
    ).toBeInTheDocument()
  })

  it('should track when submitting offer', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        to: 'stocks',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when creating draft offer', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(await screen.findByText('Sauvegarder le brouillon'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        to: 'informations',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when cancelling creation', async () => {
    renderInformationsScreen(props, contextOverride)

    await userEvent.click(await screen.findByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: true,
        isEdition: false,
        offerId: undefined,
        to: 'OfferFormHomepage',
        used: 'StickyButtons',
      }
    )
  })
})
