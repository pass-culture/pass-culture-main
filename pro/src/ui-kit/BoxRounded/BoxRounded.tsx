import cn from 'classnames'

import fullEditIcon from '@/icons/full-edit.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './BoxRounded.module.scss'

/**
 * Props for the BoxRounded component.
 */
interface BoxRoundedProps {
  /**
   * The content to be displayed inside the rounded box.
   */
  children: React.ReactNode
  /**
   * The content to be displayed at the bottom of the rounded box.
   */
  footer?: React.ReactNode
  /**
   * Custom CSS class for additional styling of the box.
   */
  className?: string
  /**
   * Callback function triggered when the modify button is clicked. If it is undefined, the edit button is not displayed
   */
  onClickModify?: () => void
}

/**
 * The BoxRounded component is used to display content within a rounded container.
 * It optionally includes a modify button, which can be used to trigger actions like editing the content.
 * @example
 * <BoxRounded onClickModify={() => console.log('Modify clicked')}>
 *   <p>This is some content inside the box.</p>
 * </BoxRounded>
 */
export const BoxRounded = ({
  children,
  footer,
  className,
  onClickModify,
}: BoxRoundedProps) => {
  const displayEditButton = Boolean(onClickModify)

  return (
    <div className={styles['expandable-box-container']}>
      <div
        className={cn(styles['expandable-box'], className, {
          [styles['expandable-box-closed']]: displayEditButton,
        })}
      >
        {displayEditButton && (
          <div className={styles['modify-button-container']}>
            <Button
              variant={ButtonVariant.TERNARY}
              onClick={onClickModify}
              icon={fullEditIcon}
            >
              Modifier
            </Button>
          </div>
        )}
        <div>{children}</div>
      </div>
      {footer && <div>{footer}</div>}
    </div>
  )
}
