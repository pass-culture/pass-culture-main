import cn from 'classnames'

import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

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
   * Custom CSS class for additional styling of the box.
   */
  className?: string
  /**
   * Callback function triggered when the modify button is clicked.
   */
  onClickModify?: () => void
  /**
   * Determines if the modify button should be displayed.
   * @default true
   */
  showButtonModify?: boolean
}

/**
 * The BoxRounded component is used to display content within a rounded container.
 * It optionally includes a modify button, which can be used to trigger actions like editing the content.
 *
 * ---
 * **Important: Use `onClickModify` to handle the action for modifying the content within the box.**
 * ---
 *
 * @param {BoxRoundedProps} props - The props for the BoxRounded component.
 * @returns {JSX.Element} The rendered BoxRounded component.
 *
 * @example
 * <BoxRounded onClickModify={() => console.log('Modify clicked')}>
 *   <p>This is some content inside the box.</p>
 * </BoxRounded>
 *
 * @accessibility
 * - **Modify Button**: The modify button is labeled "Modifier" to indicate its purpose. Ensure that it is accessible by keyboard and screen readers.
 */
export const BoxRounded = ({
  children,
  className,
  onClickModify,
  showButtonModify = true,
}: BoxRoundedProps) => {
  const displayEditButton = showButtonModify && !!onClickModify

  return (
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
      {children}
    </div>
  )
}
