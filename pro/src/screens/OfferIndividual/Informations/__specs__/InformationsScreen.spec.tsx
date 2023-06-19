import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import * as utils from 'screens/OfferIndividual/Informations/utils'
import { renderWithProviders } from 'utils/renderWithProviders'

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
jest.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: jest.fn(),
}))

const renderInformationsScreen = (
  props: IInformationsProps,
  contextValue: IOfferIndividualContext
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

  return renderWithProviders(
    <OfferIndividualContext.Provider value={contextValue}>
      <InformationsScreen {...props} />
    </OfferIndividualContext.Provider>,
    { storeOverrides, initialRouterEntries: ['/creation'] }
  )
}

const scrollIntoViewMock = jest.fn()

describe('screens:OfferIndividual::Informations', () => {
  let props: IInformationsProps
  let contextValue: IOfferIndividualContext

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

    props = {
      venueId: '',
      offererId: '',
    }

    contextValue = {
      offerId: null,
      offer: null,
      venueList: [],
      offererNames: [],
      categories,
      subCategories,
      setOffer: () => {},
      setShouldTrack: () => {},
      shouldTrack: true,
      showVenuePopin: {},
    }

    jest
      .spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
  })

  it('should render the component', async () => {
    renderInformationsScreen(props, contextValue)
    expect(
      await screen.findByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
  })

  it('should call filterCategories when no venue id is given on initial values', async () => {
    renderInformationsScreen(props, contextValue)
    await screen.findByRole('heading', { name: 'Type d’offre' })
    expect(utils.filterCategories).toHaveBeenCalledWith(
      contextValue.categories,
      contextValue.subCategories,
      CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      null
    )
  })

  describe('when a subCategory is selected', () => {
    beforeEach(async () => {
      const venue: TOfferIndividualVenue = {
        nonHumanizedId: 1,
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
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      }
      props.venueId = venue.nonHumanizedId.toString()
      contextValue.venueList = [
        venue,
        {
          nonHumanizedId: 1,
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
          hasMissingReimbursementPoint: false,
          hasCreatedOffer: true,
        },
      ]
    })

    it('should not display the full form when no venue are available', async () => {
      renderInformationsScreen(props, contextValue)
      await userEvent.selectOptions(
        await screen.findByLabelText('Catégorie'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Sous-catégorie'),
        'virtual'
      )
      expect(
        screen.queryByRole('heading', { name: 'Informations artistiques' })
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
      renderInformationsScreen(props, contextValue)
      await userEvent.selectOptions(
        await screen.findByLabelText('Catégorie'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Sous-catégorie'),
        'physical'
      )
      expect(
        screen.getByRole('heading', { name: 'Informations artistiques' })
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
    renderInformationsScreen(props, contextValue)

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')

    await userEvent.click(await screen.findByText('Étape suivante'))

    expect(scrollIntoViewMock).toHaveBeenCalledTimes(1)
    expect(scrollIntoViewMock).toHaveBeenCalledWith({
      behavior: 'auto',
      block: 'center',
      inline: 'center',
    })
  })
})
