import classnames from 'classnames'

import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'

import styles from '../SideNavLinks/SideNavLinks.module.scss'

interface HubPageNavigationProps {
  isLateralPanelOpen?: boolean
}

export const HubPageNavigation = ({
  isLateralPanelOpen = false,
}: HubPageNavigationProps) => {
  return (
    <div
      className={classnames({
        [styles['nav-links']]: true,
        [styles['nav-links-open']]: isLateralPanelOpen,
      })}
    >
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        to="/remboursements"
        iconPosition={IconPositionEnum.LEFT}
        icon={strokeRepaymentIcon}
        className={styles['back-to-partner-space-button']}
      >
        Espace Administration
      </ButtonLink>
    </div>
  )
}
