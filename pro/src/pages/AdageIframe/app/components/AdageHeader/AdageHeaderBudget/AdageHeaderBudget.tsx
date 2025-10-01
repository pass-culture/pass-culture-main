import { fromZonedTime } from 'date-fns-tz'

import { AdageHeaderLink } from '@/apiClient/adage'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './AdageHeaderBudget.module.scss'

type AdageHeaderBudgetProps = {
  logAdageLinkClick: (link: AdageHeaderLink) => void
  institutionBudget: number
}

export const AdageHeaderBudget = ({
  logAdageLinkClick,
  institutionBudget,
}: AdageHeaderBudgetProps) => {
  // TODO (nizac, 2025-09-22): To remove after the 2025-10-01
  const limitDate = fromZonedTime(
    new Date('2025-10-01T08:00:00'),
    'Europe/Paris'
  )

  if (Date.now() < limitDate.getTime()) {
    return
  }

  return (
    <div className={styles['adage-header-budget']}>
      <ButtonLink
        variant={ButtonVariant.TERNARY}
        to={`${document.referrer}adage/passculture/index`}
        isExternal
        opensInNewTab
        icon={null}
        className={styles['adage-header-budget-link']}
        onClick={() => logAdageLinkClick(AdageHeaderLink.ADAGE_LINK)}
      >
        Solde prévisionnel
      </ButtonLink>
      <div className={styles['adage-header-budget-value']}>
        {Intl.NumberFormat('fr-FR', {
          style: 'currency',
          currency: 'EUR',
          maximumFractionDigits: 0,
          minimumFractionDigits: 0, //  Some browsers need the minimum to be explicit since the defaut min value for currency is 2, in what case min > max
        }).format(institutionBudget)}
      </div>
    </div>
  )
}
