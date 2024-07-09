import { AdageHeaderLink } from 'apiClient/adage'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

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
