import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  FORM_DEFAULT_VALUES,
  setInitialFormValues,
} from 'components/OfferIndividualForm'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferIndividual, IOfferSubCategory } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import * as utils from 'screens/OfferIndividual/Informations/utils'
import { configureTestStore } from 'store/testUtils'
import { ButtonLink } from 'ui-kit'

import { IInformationsProps, Informations as InformationsScreen } from '..'

jest.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: jest.fn(),
  }
})

jest.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: jest.fn(),
}))

const renderInformationsScreen = (
  props: IInformationsProps,
  storeOverride: any,
  contextOverride: Partial<IOfferIndividualContext>,
  url = '/offre/AA/v3/creation/individuelle/informations'
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
      <MemoryRouter initialEntries={[url]}>
        <Route
          path={[
            '/offre/AA/v3/creation/individuelle/informations',
            '/offre/AA/v3/brouillon/individuelle/informations',
            '/offre/AA/v3/individuelle/informations',
          ]}
        >
          <OfferIndividualContext.Provider value={contextValue}>
            <InformationsScreen {...props} />
            <ButtonLink link={{ to: '/outside', isExternal: false }}>
              Go outside !
            </ButtonLink>
          </OfferIndividualContext.Provider>
        </Route>
        <Route path="/offre/AA/v3/creation/individuelle/stocks">
          <div>There is the stock route content</div>
        </Route>
        <Route path="/outside">
          <>
            <div>This is outside offer creation</div>
          </>
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
  let offer: IOfferIndividual

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
    offer = {
      id: 'AA',
      nonHumanizedId: 12,
      author: 'Offer author',
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      isbn: '',
      isActive: true,
      isDuo: false,
      isEducational: false,
      isEvent: true,
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
      offererId: 'A',
      offererName: '',
      performer: 'Offer performer',
      showSubType: '',
      showType: '',
      stageDirector: 'Offer stageDirector',
      speaker: 'Offer speaker',
      subcategoryId: 'physical',
      image: undefined,
      url: 'http://offer.example.com',
      externalTicketOfficeUrl: 'http://external.example.com',
      venueId: 'AA',
      venue: {
        id: 'AA',
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
      status: OfferStatus.DRAFT,
    }

    const categories = [
      {
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      },
      // we need two categories otherwise the first one is preselected and the form is dirty
      {
        id: 'B',
        proLabel: 'Catégorie B',
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
      {
        id: 'physicalB',
        categoryId: 'B',
        proLabel: 'Sous catégorie offline de B',
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

  it('should not block when from has not be touched', async () => {
    renderInformationsScreen(props, store, contextOverride)

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText('This is outside offer creation')
    ).toBeInTheDocument()
  })

  it('should block with creation block type when form has just been touched', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText('Souhaitez-vous quitter la création d’offre ?')
    ).toBeInTheDocument()
  })

  it('should block with draft creation block when form has been filled with mandatory data', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Souhaitez-vous enregistrer cette offre en brouillon avant de quitter ?'
      )
    ).toBeInTheDocument()
  })

  it('should block with draft block type when form has just been touched in draft', async () => {
    contextOverride = {
      ...contextOverride,
      offerId: offer.id,
      offer: offer,
    }

    props.initialValues = setInitialFormValues(
      offer,
      contextOverride.subCategories as IOfferSubCategory[]
    )
    renderInformationsScreen(
      props,
      store,
      contextOverride,
      '/offre/AA/v3/brouillon/individuelle/informations'
    )

    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'New name')
    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Souhaitez-vous enregistrer vos modifications avant de quitter ?'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Si vous quittez, les informations saisies ne seront pas sauvegardées dans votre brouillon.'
      )
    ).toBeInTheDocument()
  })

  it('should block with edition block type when form has just been touched in edition', async () => {
    contextOverride = {
      ...contextOverride,
      offerId: offer.id,
      offer: offer,
    }

    props.initialValues = setInitialFormValues(
      offer,
      contextOverride.subCategories as IOfferSubCategory[]
    )
    renderInformationsScreen(
      props,
      store,
      contextOverride,
      '/offre/AA/v3/individuelle/informations'
    )

    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'New name')
    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Souhaitez-vous enregistrer vos modifications avant de quitter ?'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Si vous quittez, les informations saisies ne seront pas sauvegardées.'
      )
    ).toBeInTheDocument()
  })

  it('should let submitting in block modal', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Go outside !'))
    await userEvent.click(
      screen.getByText('Enregistrer un brouillon et quitter')
    )
    expect(api.postOffer).toHaveBeenCalledTimes(1)

    expect(
      screen.getByText('This is outside offer creation')
    ).toBeInTheDocument()
  })

  it('should let quitting without submit in block modal', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Go outside !'))
    await userEvent.click(screen.getByText('Quitter sans enregistrer'))
    expect(api.postOffer).toHaveBeenCalledTimes(0)

    expect(
      screen.getByText('This is outside offer creation')
    ).toBeInTheDocument()
  })

  it('should not block when submitting minimal physical offer from action bar', async () => {
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Étape suivante'))
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
  })

  it('should not block the user when saving draft from action bar', async () => {
    // FIX ME: at first I wanna tested that user could aftewards go outside
    // but I'm not able to do it, in test the form remain dirty
    // I don't figure why, maybe because of api mocks
    renderInformationsScreen(props, store, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText(
        'Tous les champs sont obligatoires sauf mention contraire.'
      )
    ).toBeInTheDocument()
  })
})
