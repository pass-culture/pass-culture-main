import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { SimplifiedBankAccountStatus } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import * as useIsCaledonian from '@/commons/hooks/useIsCaledonian'
import { statisticsFactory } from '@/commons/utils/factories/statisticsFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IncomeCard } from '../IncomeCard'

vi.mock('@/apiClient/api', () => ({
  api: {
    getStatistics: vi.fn(),
  },
}))

const MOCK_STATISTICS = statisticsFactory({
  collectiveAndIndividualRevenueYear: String(new Date().getFullYear()),
  lastYear: String(new Date().getFullYear()),
})

const mockLogEvent = vi.fn()

const renderIncomeCard = (
  props?: {
    venueId?: number
    bankAccountStatus?: SimplifiedBankAccountStatus | null
  },
  initialRouterEntries?: string[]
) => {
  const { venueId = 1, bankAccountStatus = SimplifiedBankAccountStatus.VALID } =
    props ?? {}

  renderWithProviders(
    <IncomeCard venueId={venueId} bankAccountStatus={bankAccountStatus} />,
    {
      user: sharedCurrentUserFactory(),
      storeOverrides: {
        offerer: currentOffererFactory(),
      },
      initialRouterEntries,
    }
  )
}

describe('IncomeCard', () => {
  beforeEach(() => {
    vi.spyOn(useIsCaledonian, 'useIsCaledonian').mockReturnValue(false)
    vi.spyOn(api, 'getStatistics').mockResolvedValue(MOCK_STATISTICS)
  })

  it('should display an error banner when the API call fails', async () => {
    vi.spyOn(api, 'getStatistics').mockRejectedValueOnce(new Error('error'))

    renderIncomeCard()

    expect(
      await screen.findByText(
        "Impossible de charger les données de chiffre d'affaires"
      )
    ).toBeVisible()
  })

  it('should display a banner to add a bank account when bank account status is null', async () => {
    renderIncomeCard({ bankAccountStatus: null })

    expect(
      await screen.findByText(
        'Aucun compte bancaire configuré pour percevoir vos remboursements'
      )
    ).toBeVisible()
  })

  it('should display a banner for incomplete bank account when status is PENDING_CORRECTIONS', async () => {
    renderIncomeCard({
      bankAccountStatus: SimplifiedBankAccountStatus.PENDING_CORRECTIONS,
    })

    expect(await screen.findByText('Compte bancaire incomplet')).toBeVisible()
  })

  it('should display a banner for pending verification when status is PENDING', async () => {
    renderIncomeCard({
      bankAccountStatus: SimplifiedBankAccountStatus.PENDING,
    })

    expect(
      await screen.findByText(
        'Vos coordonnées bancaires sont en cours de vérification par nos équipes.'
      )
    ).toBeVisible()
  })

  it('should display the revenue section with total formatted in EUR', async () => {
    renderIncomeCard()

    expect(await screen.findByText('Remboursement')).toBeVisible()
    expect(screen.getByText('Individuel et collectif')).toBeVisible()
    expect(screen.getByText(/Chiffre d.affaire total/)).toBeVisible()
    expect(screen.getByText(/11 430,23/)).toBeVisible()
  })

  it('should display a link to financial management', async () => {
    renderIncomeCard()

    expect(
      await screen.findByRole('link', {
        name: 'Accéder à la gestion financière',
      })
    ).toBeVisible()
  })

  it('should display the individual revenue total when venue has only individual revenue', async () => {
    const currentYear = new Date().getFullYear()
    vi.spyOn(api, 'getStatistics').mockResolvedValueOnce(
      statisticsFactory({
        individualRevenueOnlyYear: String(currentYear),
        lastYear: String(currentYear),
      })
    )

    renderIncomeCard()

    expect(await screen.findByText(/1 000/)).toBeVisible()
  })

  it('should display the collective revenue total when venue has only collective revenue', async () => {
    const currentYear = new Date().getFullYear()
    vi.spyOn(api, 'getStatistics').mockResolvedValueOnce(
      statisticsFactory({
        collectiveRevenueOnlyYear: String(currentYear),
        lastYear: String(currentYear),
      })
    )

    renderIncomeCard()

    expect(await screen.findByText(/3 000/)).toBeVisible()
  })

  it('should display the total in Pacific Franc (F) when isCaledonian is true', async () => {
    vi.spyOn(useIsCaledonian, 'useIsCaledonian')
      .mockReturnValueOnce(true) // first call spinner
      .mockReturnValueOnce(true)

    renderIncomeCard()

    expect(await screen.findByText(/F/)).toBeVisible()
    expect(screen.queryByText(/€/)).not.toBeInTheDocument()
  })

  it('should display the total in EUR when isCaledonian is false', async () => {
    renderIncomeCard()

    expect(await screen.findByText(/€/)).toBeVisible()
    expect(screen.queryByText(/F/)).not.toBeInTheDocument()
  })

  it('should log CLICKED_ADD_BANK_ACCOUNT when clicking on add bank account link', async () => {
    const user = userEvent.setup()
    vi.spyOn(useAnalytics, 'useAnalytics').mockReturnValue({
      logEvent: mockLogEvent,
    })

    renderIncomeCard({ bankAccountStatus: null }, ['/accueil'])

    const link = await screen.findByRole('link', {
      name: 'Ajouter un compte bancaire',
    })
    expect(link).toBeVisible()

    await user.click(link)

    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT,
      {
        from: '/accueil',
        venueId: 1,
      }
    )
  })

  it('should log CLICKED_BANK_ACCOUNT_HAS_PENDING_CORRECTIONS when clicking on pending corrections link', async () => {
    const user = userEvent.setup()
    vi.spyOn(useAnalytics, 'useAnalytics').mockReturnValue({
      logEvent: mockLogEvent,
    })

    renderIncomeCard(
      {
        bankAccountStatus: SimplifiedBankAccountStatus.PENDING_CORRECTIONS,
      },
      ['/accueil']
    )

    const link = await screen.findByRole('link', {
      name: 'Voir les corrections attendues',
    })
    expect(link).toBeVisible()

    await user.click(link)

    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
      {
        from: '/accueil',
        venueId: 1,
      }
    )
  })
})
