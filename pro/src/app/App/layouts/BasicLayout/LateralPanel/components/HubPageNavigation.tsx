import classnames from 'classnames'

import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'

import styles from './SideNavLinks.module.scss'

interface HubPageNavigationProps {
  isLateralPanelOpen?: boolean
}

export const HubPageNavigation = ({
  isLateralPanelOpen = false,
}: HubPageNavigationProps) => {
  return (
    <div
      className={classnames(
        {
          [styles['nav-links']]: true,
          [styles['nav-links-open']]: isLateralPanelOpen,
        },
        styles['back-to-admin']
      )}
    >
      <Button
        as="a"
        variant={ButtonVariant.SECONDARY}
        to="/remboursements"
        iconPosition={IconPositionEnum.LEFT}
        icon={strokeRepaymentIcon}
        label="Espace Administration"
      />
    </div>
  )
}
