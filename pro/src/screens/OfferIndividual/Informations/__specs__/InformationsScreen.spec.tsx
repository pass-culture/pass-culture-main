import '@testing-library/jest-dom'

import * as utils from 'screens/OfferIndividual/Informations/utils'

import { IInformationsProps, Informations as InformationsScreen } from '..'
import { render, screen } from '@testing-library/react'

import { CATEGORY_STATUS } from 'core/Offers'
import { FORM_DEFAULT_VALUES } from 'new_components/OfferIndividualForm'
import { MemoryRouter } from 'react-router'
import { Provider } from 'react-redux'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import React from 'react'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

jest.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: jest.fn(),
  }
})

const renderInformationsScreen = (
  props: IInformationsProps,
  storeOverride: any
) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <InformationsScreen {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('screens:OfferCreation::Informations', () => {
  let props: IInformationsProps
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
    const categories = [
      {
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      },
    ]
    const subCategories = [
      {
        id: 'A-A',
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
        id: 'A-B',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]

    props = {
      createOfferAdapter: jest.fn(),
      initialValues: FORM_DEFAULT_VALUES,
      offererNames: [],
      venueList: [],
      categories,
      subCategories,
    }

    jest
      .spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
  })

  it('should render the component', async () => {
    renderInformationsScreen(props, store)
    expect(
      await screen.findByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
  })

  it('should call filterCategories when no venue id is given on initial values', async () => {
    renderInformationsScreen(props, store)
    await screen.findByRole('heading', { name: 'Type d’offre' })
    expect(utils.filterCategories).toHaveBeenCalledWith(
      props.categories,
      props.subCategories,
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
    props.venueList = [
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

    renderInformationsScreen(props, store)
    await screen.findByRole('heading', { name: 'Type d’offre' })
    expect(utils.filterCategories).toHaveBeenCalledWith(
      props.categories,
      props.subCategories,
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
      props.venueList = [
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
      renderInformationsScreen(props, store)
      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une catégorie'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une sous-catégorie'),
        'A-A'
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
      renderInformationsScreen(props, store)
      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une catégorie'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Choisir une sous-catégorie'),
        'A-B'
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
})
