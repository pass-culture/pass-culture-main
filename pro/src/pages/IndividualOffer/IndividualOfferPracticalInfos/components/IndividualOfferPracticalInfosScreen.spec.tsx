import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { SubcategoryIdEnum, WithdrawalTypeEnum } from '@/apiClient/v1'
import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import type { IndividualOfferPracticalInfosFormProps } from './IndividualOfferPracticalInfosForm/IndividualOfferPracticalInfosForm'
import { IndividualOfferPracticalInfosScreen } from './IndividualOfferPracticalInfosScreen'

vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
}))

Element.prototype.scrollIntoView = vi.fn()

function renderIndividualOfferPracticalInfosScreen(
  props?: Partial<IndividualOfferPracticalInfosFormProps>
) {
  renderWithProviders(
    <IndividualOfferContext.Provider
      value={individualOfferContextValuesFactory({
        categories: [],
        subCategories: [
          subcategoryFactory({
            id: SubcategoryIdEnum.CONCERT,
            canBeWithdrawable: true,
          }),
        ],
      })}
    >
      <IndividualOfferPracticalInfosScreen
        offer={getIndividualOfferFactory()}
        stocks={[]}
        {...props}
      />
    </IndividualOfferContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
    }
  )
}

describe('IndividualOfferPracticalInfosScreen', () => {
  it('should show the form action bar in creation mode', async () => {
    renderIndividualOfferPracticalInfosScreen()

    await waitFor(() => {
      screen.getByRole('heading', { name: 'Informations pratiques' })
    })

    expect(
      screen.getByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()
  })

  it('should open the warning dialog when submitting the form on an offer with active booking if the withdrawal info were modified', async () => {
    renderIndividualOfferPracticalInfosScreen({
      offer: getIndividualOfferFactory({
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: 10,
        withdrawalDetails: 'test',
        bookingAllowedDatetime: null,
        hasPendingBookings: true,
        subcategoryId: SubcategoryIdEnum.CONCERT,
        bookingContact: 'test@test.co',
      }),
    })

    await waitFor(() => {
      screen.getByRole('heading', { name: 'Informations pratiques' })
    })

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Retrait sur place (guichet, comptoir...)',
      })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer et continuer' })
    )

    expect(
      screen.getByRole('heading', {
        name: 'Les changements vont s’appliquer à l’ensemble des réservations en cours associées',
      })
    ).toBeInTheDocument()
  })
})
