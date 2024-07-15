import { screen, within } from '@testing-library/react'

import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import {
  categoryFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  UsefulInformationScreen,
  UsefulInformationScreenProps,
} from '../UsefulInformationScreen'

const renderUsefulInformationScreen = (
  props: UsefulInformationScreenProps,
  contextValue: IndividualOfferContextValues
) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <UsefulInformationScreen {...props} />
    </IndividualOfferContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
    }
  )
}

describe('screens:IndividualOffer::UsefulInformation', () => {
  let props: UsefulInformationScreenProps
  let contextValue: IndividualOfferContextValues

  beforeEach(() => {
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
        canBeDuo: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      subcategoryFactory({
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: ['ean'],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    props = {
      venues: [],
    }

    contextValue = individualOfferContextValuesFactory({
      categories,
      subCategories,
    })
  })

  it('should render the component', async () => {
    renderUsefulInformationScreen(props, contextValue)
    expect(
      await screen.findByRole('heading', { name: 'Retrait de l’offre' })
    ).toBeInTheDocument()

    const withdrawalDetails = await screen.findByTestId(
      'wrapper-withdrawalDetails'
    )
    expect(withdrawalDetails).toBeInTheDocument()

    expect(
      within(withdrawalDetails).getByText('Informations de retrait')
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', { name: 'Modalités d’accessibilité' })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', { name: 'Notifications' })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', { name: 'Lien pour le grand public' })
    ).toBeInTheDocument()

    const externalTicketOfficeUrl = await screen.findByTestId(
      'wrapper-externalTicketOfficeUrl'
    )
    expect(externalTicketOfficeUrl).toBeInTheDocument()
    expect(
      within(externalTicketOfficeUrl).getByText(
        'URL de votre site ou billetterie'
      )
    ).toBeInTheDocument
  })
})
