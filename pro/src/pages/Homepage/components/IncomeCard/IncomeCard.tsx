import { useLocation } from 'react-router'

import type {
  CollectiveRevenue,
  IndividualRevenue,
  TotalRevenue,
} from '@/apiClient/v1'
import { SimplifiedBankAccountStatus } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullNextIcon from '@/icons/full-next.svg'
import strokeClockIcon from '@/icons/stroke-clock.svg'
import { useIncome } from '@/pages/Reimbursements/Income/useIncome'
import {
  isCollectiveAndIndividualRevenue,
  isCollectiveRevenue,
} from '@/pages/Reimbursements/Income/utils'
import { Card } from '@/ui-kit/Card/Card'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IncomeCard.module.scss'

interface IncomeCardProps {
  venueId: number
  bankAccountStatus: SimplifiedBankAccountStatus | null
}

const BankAccountBanner = ({
  venueId,
  bankAccountStatus,
}: IncomeCardProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  switch (bankAccountStatus) {
    case null:
      return (
        <Banner
          title="Aucun compte bancaire configuré pour percevoir vos remboursements"
          variant={BannerVariants.ERROR}
          actions={[
            {
              href: '/remboursements/informations-bancaires',
              label: 'Ajouter un compte bancaire',
              type: 'link',
              icon: fullNextIcon,
              onClick: () => {
                logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
                  from: location.pathname,
                  venueId,
                })
              },
            },
          ]}
        />
      )
    case SimplifiedBankAccountStatus.PENDING_CORRECTIONS:
      return (
        <Banner
          title="Compte bancaire incomplet"
          variant={BannerVariants.ERROR}
          actions={[
            {
              href: '/remboursements/informations-bancaires',
              label: 'Voir les corrections attendues',
              type: 'link',
              icon: fullNextIcon,
              onClick: () => {
                logEvent(
                  BankAccountEvents.CLICKED_BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
                  {
                    from: location.pathname,
                    venueId,
                  }
                )
              },
            },
          ]}
        />
      )
    case SimplifiedBankAccountStatus.PENDING:
      return (
        <Banner
          title="Vos coordonnées bancaires sont en cours de vérification par nos équipes."
          variant={BannerVariants.DEFAULT}
        />
      )
    default:
      return null
  }
}

export const IncomeCard = ({
  venueId,
  bankAccountStatus,
}: IncomeCardProps): JSX.Element | null => {
  const currentYear = new Date().getFullYear()
  const isCaledonian = useIsCaledonian()

  const { incomeByYear, isIncomeLoading, incomeApiError } = useIncome([
    String(venueId),
  ])

  if (isIncomeLoading) {
    return (
      <Card>
        <Spinner />
      </Card>
    )
  }

  if (incomeApiError) {
    return (
      <Card>
        <Banner
          title="Impossible de charger les données de chiffre d'affaires"
          variant={BannerVariants.ERROR}
        />
      </Card>
    )
  }

  const currentYearIncome = incomeByYear?.[currentYear]

  const income = currentYearIncome?.revenue as
    | TotalRevenue
    | CollectiveRevenue
    | IndividualRevenue
    | undefined

  const getIncomeTotal = (
    income: TotalRevenue | CollectiveRevenue | IndividualRevenue | undefined
  ): number => {
    if (!income) {
      return 0
    }
    if (isCollectiveAndIndividualRevenue(income)) {
      return income.total
    }
    if (isCollectiveRevenue(income)) {
      return income.collective
    }
    return income.individual
  }

  const total = getIncomeTotal(income)

  const isEmptyState =
    bankAccountStatus === SimplifiedBankAccountStatus.VALID && total === 0

  const formattedTotal = isCaledonian
    ? formatPacificFranc(convertEuroToPacificFranc(total))
    : total.toLocaleString('fr-FR', {
        style: 'currency',
        currency: 'EUR',
      })

  const cardHeader = (
    <Card.Header title="Remboursement" subtitle="Individuel et collectif" />
  )

  return (
    <Card>
      {!isEmptyState && cardHeader}

      <Card.Content>
        <BankAccountBanner
          venueId={venueId}
          bankAccountStatus={bankAccountStatus}
        />

        {isEmptyState && (
          <div className={styles['income-card-empty']}>
            <SvgIcon
              className={styles['income-card-empty-icon']}
              src={strokeClockIcon}
              alt=""
              width="57"
            />
            {cardHeader}
            <p className={styles['income-card-empty-text']}>
              Vos informations financières seront prochainement affichées ici.
            </p>
          </div>
        )}

        {bankAccountStatus === SimplifiedBankAccountStatus.VALID &&
          total > 0 && (
            <div className={styles['income-card-amount']}>
              <p className={styles['income-card-label']}>
                Chiffre d'affaire total {currentYear}
              </p>
              <Tag variant={TagVariant.SUCCESS} label={formattedTotal} />
            </div>
          )}
      </Card.Content>

      {bankAccountStatus === SimplifiedBankAccountStatus.VALID && total > 0 && (
        <Card.Footer>
          <Button
            as="a"
            to="/remboursements/revenus"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.DEFAULT}
            label="Accéder à la gestion financière"
          />
        </Card.Footer>
      )}
    </Card>
  )
}
