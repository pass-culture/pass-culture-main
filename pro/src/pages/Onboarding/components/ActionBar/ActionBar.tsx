import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import fullLeftIcon from 'icons/full-left.svg'
import fullRightIcon from 'icons/full-right.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from './ActionBar.module.scss'

// These props can have either "withNextButton" or "withValidateButton" but not both
type ActionBarProps = {
  hasSideNav?: boolean
  disableRightButton?: boolean
  withNextButton?: boolean
  onLeftButtonClick: (evt: React.MouseEvent<HTMLButtonElement>) => void
  onRightButtonClick?: (evt: React.MouseEvent<HTMLButtonElement>) => void
}

export const ActionBar = ({
  hasSideNav = false,
  disableRightButton = false,
  withNextButton = false,
  onLeftButtonClick,
  onRightButtonClick,
}: ActionBarProps): JSX.Element => {
  return (
    <ActionsBarSticky
      hasSideNav={hasSideNav}
      className={styles['action-bar-fixed']}
    >
      <ActionsBarSticky.Left>
        <Button
          icon={fullLeftIcon}
          variant={ButtonVariant.SECONDARY}
          onClick={onLeftButtonClick}
        >
          Retour
        </Button>
      </ActionsBarSticky.Left>
      {onRightButtonClick && (
        <ActionsBarSticky.Right>
          <Button
            type="submit"
            icon={withNextButton ? fullRightIcon : undefined}
            iconPosition={IconPositionEnum.RIGHT}
            disabled={disableRightButton}
            onClick={onRightButtonClick}
          >
            {withNextButton ? 'Étape suivante' : 'Valider'}
          </Button>
        </ActionsBarSticky.Right>
      )}
    </ActionsBarSticky>
  )
}
