import { AdageHeaderLink } from 'apiClient/adage'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageHeaderBudget.module.scss'

type AdageHeaderBudgetProps = {
  logAdageLinkClick: (link: AdageHeaderLink) => void
  institutionBudget: number
}

export default function AdageHeaderBudget({
  logAdageLinkClick,
  institutionBudget,
}: AdageHeaderBudgetProps) {
  return (
    <div className={styles['adage-header-budget']}>
      <ButtonLink
        variant={ButtonVariant.TERNARY}
        link={{
          to: `${document.referrer}adage/passculture/index`,
          isExternal: true,
          target: '_blank',
        }}
        className={styles['adage-header-budget-link']}
        onClick={() => logAdageLinkClick(AdageHeaderLink.ADAGE_LINK)}
      >
        <SvgIcon
          width="16"
          alt="Nouvelle fenêtre"
          src={fullLinkIcon}
          className={styles['adage-header-budget-icon']}
        />
        Solde prévisionnel
      </ButtonLink>
      <div className={styles['adage-header-budget-value']}>
        {Intl.NumberFormat('fr-FR', {
          style: 'currency',
          currency: 'EUR',
          maximumFractionDigits: 0,
        }).format(institutionBudget)}
      </div>
    </div>
  )
}
