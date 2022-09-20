import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { FORM_DEFAULT_VALUES } from 'new_components/OfferIndividualForm'
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
  },
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

describe('screens:OfferCreation::Informations', () => {
  let props: IInformationsProps
  let store: any
  let contextValue: IOfferIndividualContext

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

    props = {
      initialValues: FORM_DEFAULT_VALUES,
    }

    contextValue = {
      offerId: null,
      offer: null,
      venueList: [],
      offererNames: [],
      categories,
      subCategories,
      reloadOffer: () => {},
    }

    jest
      .spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
  })

  it('should render the component', async () => {
    renderInformationsScreen(props, store, contextValue)
    expect(
      await screen.findByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
  })

  it('should call filterCategories when no venue id is given on initial values', async () => {
    renderInformationsScreen(props, store, contextValue)
    await screen.findByRole('heading', { name: 'Type d’offre' })
    expect(utils.filterCategories).toHaveBeenCalledWith(
      contextValue.categories,
      contextValue.subCategories,
      undefined
    )
  })

  it('should call filterCategories when venueId is given on initial values', async () => {
    const venue: TOfferIndividualVenue = {
      id: 'AA',
      name: 'Lieu AA',
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
    props.initialValues.venueId = venue.id
    contextValue.venueList = [
      venue,
      {
        id: 'BB',
        name: 'Lieu BB',
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
      },
    ]

    renderInformationsScreen(props, store, contextValue)
    await screen.findByRole('heading', { name: 'Type d’offre' })
    expect(utils.filterCategories).toHaveBeenCalledWith(
      contextValue.categories,
      contextValue.subCategories,
      venue
    )
  })

  describe('when a subCategory is selected', () => {
    beforeEach(async () => {
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
      props.initialValues.venueId = venue.id
      contextValue.venueList = [
        venue,
        {
          id: 'BB',
          name: 'Lieu offline BB',
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
        },
      ]
    })

    it('should not display the full form when no venue are available', async () => {
      renderInformationsScreen(props, store, contextValue)
      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une catégorie'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une sous-catégorie'),
        'virtual'
      )
      expect(
        screen.queryByRole('heading', { name: 'Informations générales' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('heading', { name: 'Accessibilité' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('heading', { name: 'Lien pour le grand public' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('heading', { name: 'Notifications' })
      ).not.toBeInTheDocument()
    })

    it('should display the full form when a venue is available', async () => {
      renderInformationsScreen(props, store, contextValue)
      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une catégorie'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une sous-catégorie'),
        'physical'
      )
      expect(
        screen.getByRole('heading', { name: 'Informations générales' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: 'Accessibilité' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: 'Lien pour le grand public' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: 'Notifications' })
      ).toBeInTheDocument()
    })
  })

  it('should scroll to error', async () => {
    renderInformationsScreen(props, store, contextValue)

    const categorySelect = await screen.findByLabelText('Choisir une catégorie')
    await userEvent.selectOptions(categorySelect, 'A')

    await userEvent.click(await screen.findByText('Suivant'))

    expect(scrollIntoViewMock).toHaveBeenCalledTimes(1)
    expect(scrollIntoViewMock).toHaveBeenCalledWith({
      behavior: 'auto',
      block: 'center',
      inline: 'center',
    })
  })

  describe('submit', () => {
    beforeEach(async () => {
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
      contextValue.venueList = [
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
      ]
      contextValue.offererNames = [{ id: 'A', name: 'mon offerer A' }]
      props = {
        initialValues: FORM_DEFAULT_VALUES,
      }
    })
    it('should submit minimal physical offer', async () => {
      renderInformationsScreen(props, store, contextValue)

      const categorySelect = await screen.findByLabelText(
        'Choisir une catégorie'
      )
      await userEvent.selectOptions(categorySelect, 'A')
      const subCategorySelect = screen.getByLabelText(
        'Choisir une sous-catégorie'
      )
      await userEvent.selectOptions(subCategorySelect, 'physical')
      const nameField = screen.getByLabelText("Titre de l'offre")
      await userEvent.type(nameField, 'Le nom de mon offre')

      await userEvent.click(await screen.findByText('Suivant'))

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
    })

    it('should submit minimal virtual offer', async () => {
      renderInformationsScreen(props, store, contextValue)

      const categorySelect = await screen.findByLabelText(
        'Choisir une catégorie'
      )
      await userEvent.selectOptions(categorySelect, 'A')
      const subCategorySelect = screen.getByLabelText(
        'Choisir une sous-catégorie'
      )
      await userEvent.selectOptions(subCategorySelect, 'virtual')
      const nameField = screen.getByLabelText("Titre de l'offre")
      await userEvent.type(nameField, 'Le nom de mon offre')

      const urlField = await screen.findByLabelText('URL d’accès à l’offre')

      await userEvent.type(urlField, 'http://example.com/')

      await userEvent.click(await screen.findByText('Suivant'))

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
    })
  })
})
