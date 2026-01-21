import { AdageHeaderLink } from '@/apiClient/adage'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import styles from './AdageHeaderBudget.module.scss'

type AdageHeaderBudgetProps = {
  logAdageLinkClick: (link: AdageHeaderLink) => void
  institutionBudget: number
}

export const AdageHeaderBudget = ({
  logAdageLinkClick,
  institutionBudget,
}: AdageHeaderBudgetProps) => {
  return (
    <div className={styles['adage-header-budget']}>
      <Button
        as="a"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        to={`${document.referrer}adage/passculture/index`}
        isExternal
        opensInNewTab
        className={styles['adage-header-budget-link']}
        onClick={() => logAdageLinkClick(AdageHeaderLink.ADAGE_LINK)}
        label="Solde prévisionnel"
      />
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
