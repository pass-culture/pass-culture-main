import cn from 'classnames'

import { AccessibilityEnum } from '@/commons/core/shared/types'
import strokeAccessibilityBrainIcon from '@/icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEarIcon from '@/icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEyeIcon from '@/icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLegIcon from '@/icons/stroke-accessibility-leg.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './AccessibilityLabel.module.scss'

/**
 * Props for the AccessibilityLabel component.
 */
interface AccessibilityLabelProps {
  /**
   * Custom CSS class for additional styling of the accessibility label.
   */
  className?: string
  /**
   * The accessibility type to display.
   */
  name: AccessibilityEnum
}

/**
 * The AccessibilityLabel component displays an accessibility label with an optional icon based on the type of accessibility.
 * This helps users understand which accessibility feature applies to a specific element or section.
 *
 * ---
 * **Important: Use the `name` prop to provide the correct type of accessibility information.**
 * ---
 *
 * @param {AccessibilityLabelProps} props - The props for the AccessibilityLabel component.
 * @returns {JSX.Element} The rendered AccessibilityLabel component.
 *
 * @example
 * <AccessibilityLabel name={AccessibilityEnum.VISUAL} />
 *
 * @accessibility
 * - **Visual Icon**: Each icon is used to provide a visual indication of the type of accessibility supported. Make sure that the icons are recognizable and provide sufficient context.
 * - **Labeling**: The `labelData` object is used to associate the accessibility type with a specific label and icon to make the information more understandable for users.
 */
export const AccessibilityLabel = ({
  className,
  name,
}: AccessibilityLabelProps): JSX.Element => {
  const labelData = {
    [AccessibilityEnum.AUDIO]: {
      label: 'Auditif',
      svg: strokeAccessibilityEarIcon,
    },
    [AccessibilityEnum.MENTAL]: {
      label: 'Psychique ou cognitif',
      svg: strokeAccessibilityBrainIcon,
    },
    [AccessibilityEnum.MOTOR]: {
      label: 'Moteur',
      svg: strokeAccessibilityLegIcon,
    },
    [AccessibilityEnum.VISUAL]: {
      label: 'Visuel',
      svg: strokeAccessibilityEyeIcon,
    },
    [AccessibilityEnum.NONE]: {
      label: 'Non accessible',
    },
  }[name]

  return (
    <div className={cn(styles['accessibility-label'], className)}>
      {labelData.svg && (
        <SvgIcon
          src={labelData.svg}
          className={styles['icon']}
          width="24"
          alt=""
        />
      )}
      <span className={styles['text']}>{labelData.label}</span>
    </div>
  )
}
