import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import {
  categoryFactory,
  getIndividualOfferFactory,
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
      offer: getIndividualOfferFactory({
        id: 3,
      }),
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

  it('should submit the form with correct payload', async () => {
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      getIndividualOfferFactory({
        id: 12,
      })
    )

    renderUsefulInformationScreen(props, contextValue)

    await userEvent.type(
      screen.getByLabelText(/Informations de retrait/),
      'My information'
    )

    await userEvent.click(screen.getByLabelText(/Visuel/))
    await userEvent.click(screen.getByLabelText(/Psychique ou cognitif/))

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(api.patchOffer).toHaveBeenCalledOnce()
    expect(api.patchOffer).toHaveBeenCalledWith(3, {
      audioDisabilityCompliant: true,
      bookingContact: undefined,
      bookingEmail: null,
      description: undefined,
      durationMinutes: undefined,
      externalTicketOfficeUrl: undefined,
      extraData: undefined,
      isDuo: undefined,
      isNational: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      name: undefined,
      shouldSendMail: false,
      url: undefined,
      visualDisabilityCompliant: false,
      withdrawalDelay: undefined,
      withdrawalDetails: 'My information',
      withdrawalType: undefined,
    })
  })
})
