import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { VenueListItemResponseModel } from 'apiClient/v1'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'core/Finances/constants'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import * as filterCategories from 'screens/IndividualOffer/InformationsScreen/utils/filterCategories/filterCategories'
import {
  categoryFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  InformationsScreen,
  InformationsScreenProps,
} from '../InformationsScreen'

vi.mock('screens/IndividualOffer/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

vi.mock('apiClient/api', () => ({
  api: {
    postOffer: vi.fn(),
  },
}))
vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

const renderInformationsScreen = (
  props: InformationsScreenProps,
  contextValue: IndividualOfferContextValues
) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <InformationsScreen {...props} />
    </IndividualOfferContext.Provider>,
    { user: sharedCurrentUserFactory(), initialRouterEntries: ['/creation'] }
  )
}

const scrollIntoViewMock = vi.fn()

describe('screens:IndividualOffer::Informations', () => {
  let props: InformationsScreenProps
  let contextValue: IndividualOfferContextValues

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const categories = [
      categoryFactory({
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      }),
    ]
    const subCategories = [
      subcategoryFactory({
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
      }),
      subcategoryFactory({
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
      }),
    ]

    props = {
      venueId: '',
      offererId: '',
      offererNames: [],
      venueList: [],
    }

    contextValue = individualOfferContextValuesFactory({
      categories,
      subCategories,
      offer: null,
    })

    vi.spyOn(filterCategories, 'filterCategories')
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

    expect(filterCategories.filterCategories).toHaveBeenCalledWith(
      contextValue.categories,
      contextValue.subCategories,
      CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      null
    )
  })

  describe('when a subCategory is selected', () => {
    beforeEach(() => {
      const venue1: VenueListItemResponseModel = venueListItemFactory()
      const venue2: VenueListItemResponseModel = venueListItemFactory()

      props.venueId = venue1.id.toString()
      props.venueList = [venue1, venue2]
    })

    it('should not display the full form when no venue are available', async () => {
      renderInformationsScreen(props, contextValue)
      await userEvent.selectOptions(
        await screen.findByLabelText('Catégorie *'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Sous-catégorie *'),
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
        await screen.findByLabelText('Catégorie *'),
        'A'
      )

      await userEvent.selectOptions(
        await screen.findByLabelText('Sous-catégorie *'),
        'physical'
      )
      expect(
        screen.getByRole('heading', { name: 'Informations artistiques' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: 'Accessibilité' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: 'Notifications' })
      ).toBeInTheDocument()
    })
  })

  it('should scroll to error', async () => {
    renderInformationsScreen(props, contextValue)

    const categorySelect = await screen.findByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')

    await userEvent.click(await screen.findByText('Enregistrer et continuer'))

    expect(scrollIntoViewMock).toHaveBeenCalledTimes(1)
    expect(scrollIntoViewMock).toHaveBeenCalledWith({
      behavior: 'auto',
      block: 'center',
      inline: 'center',
    })
  })
})
