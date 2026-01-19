import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { SubcategoryIdEnum, WithdrawalTypeEnum } from '@/apiClient/v1'
import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import * as useOfferWizardMode from '@/commons/hooks/useOfferWizardMode'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualOfferPracticalInfosScreen,
  type IndividualOfferPracticalInfosScreenProps,
} from './IndividualOfferPracticalInfosScreen'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOffer: vi.fn(),
    patchOffer: vi.fn(),
  },
}))

vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
}))

const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

Element.prototype.scrollIntoView = vi.fn()

const LABELS = {
  heading: 'Informations pratiques',
  saveButton: 'Enregistrer et continuer',
}

function renderIndividualOfferPracticalInfosScreen(
  props?: Partial<IndividualOfferPracticalInfosScreenProps>,
  features?: string[]
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
      features,
    }
  )
}

describe('IndividualOfferPracticalInfosScreen', () => {
  it('should show the form action bar in creation mode', async () => {
    renderIndividualOfferPracticalInfosScreen()

    await waitFor(() => {
      screen.getByRole('heading', { name: LABELS.heading })
    })

    expect(
      screen.getByRole('button', { name: LABELS.saveButton })
    ).toBeInTheDocument()
  })

  it('should open the warning dialog when submitting the form on an offer with active booking if the withdrawal info were modified', async () => {
    renderIndividualOfferPracticalInfosScreen({
      offer: getIndividualOfferFactory({
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: 10,
        withdrawalDetails: 'test',
        hasPendingBookings: true,
        subcategoryId: SubcategoryIdEnum.CONCERT,
        bookingContact: 'test@test.co',
      }),
    })

    await waitFor(() => {
      screen.getByRole('heading', { name: LABELS.heading })
    })

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Retrait sur place (guichet, comptoir...)',
      })
    )

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.saveButton })
    )

    expect(
      screen.getByRole('heading', {
        name: 'Les changements vont s’appliquer à l’ensemble des réservations en cours associées',
      })
    ).toBeInTheDocument()
  })

  it('should update the offer when submitting the form', async () => {
    renderIndividualOfferPracticalInfosScreen()

    const updateSpy = vi
      .spyOn(api, 'patchOffer')
      .mockResolvedValue(getIndividualOfferFactory())

    await waitFor(() => {
      screen.getByRole('heading', { name: LABELS.heading })
    })

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.saveButton })
    )

    expect(updateSpy).toHaveBeenCalled()
  })

  it('should navigate to the stocks page whern clicking previous while on creation mode', async () => {
    renderIndividualOfferPracticalInfosScreen({})

    await waitFor(() => {
      screen.getByRole('heading', { name: LABELS.heading })
    })

    await userEvent.click(screen.getByRole('button', { name: 'Retour' }))

    expect(mockNavigate).toHaveBeenCalledWith(
      expect.stringContaining('/creation/horaires')
    )
  })

  it('should navigate to the practical info summary page whern clicking cancel while on edition mode', async () => {
    vi.spyOn(useOfferWizardMode, 'useOfferWizardMode').mockImplementation(
      () => OFFER_WIZARD_MODE.EDITION
    )

    renderIndividualOfferPracticalInfosScreen({})

    await waitFor(() => {
      screen.getByRole('heading', { name: LABELS.heading })
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler et quitter' })
    )

    expect(mockNavigate).toHaveBeenCalledWith(
      expect.stringContaining('/informations_pratiques')
    )
  })
})
