import cn from 'classnames'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { RadioButtonCheckedSVG } from './RadioButtonCheckedSVG'
import { RadioButtonUncheckedSVG } from './RadioButtonUncheckedSVG'
import styles from './RadioButtonWithImage.module.scss'

/**
 * Props for the RadioButtonWithImage component.
 */
interface RadioButtonWithImageProps {
  /**
   * The name of the radio button group.
   */
  name: string
  /**
   * Indicates if the radio button is currently selected.
   */
  isChecked: boolean
  /**
   * The icon to display alongside the radio button.
   */
  icon?: string
  /**
   * The label text for the radio button.
   */
  label: string | React.ReactNode
  /**
   * An optional description for the radio button.
   */
  description?: string
  /**
   * Callback function triggered when the radio button value changes.
   */
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  /**
   * Custom CSS class for additional styling of the radio button.
   */
  className?: string
  /**
   * Indicates if the radio button is disabled.
   * @default false
   */
  disabled?: boolean
  /**
   * The value of the radio button.
   */
  value: string
  /**
   * Custom test ID for targeting the component in tests.
   */
  dataTestid?: string
}

/**
 * The RadioButtonWithImage component is a custom radio button that includes an image and optional description.
 * It is intended to provide a more visually appealing way to present radio button options.
 *
 * ---
 * **Important: Use `isChecked` to control the selection state of the radio button, and `onChange` to handle state changes.**
 * ---
 *
 * @param {RadioButtonWithImageProps} props - The props for the RadioButtonWithImage component.
 * @returns {JSX.Element} The rendered RadioButtonWithImage component.
 *
 * @example
 * <RadioButtonWithImage
 *   name="options"
 *   isChecked={true}
 *   icon="/path/to/icon.svg"
 *   label="Option 1"
 *   value="option1"
 *   onChange={(e) => console.log(e.target.value)}
 * />
 *
 * @accessibility
 * - **Label and Description**: Ensure the `label` and `description` are descriptive enough to convey the purpose of the radio button to all users, including those using assistive technologies.
 * - **Keyboard Navigation**: The radio button should be focusable and selectable using the keyboard, allowing for seamless navigation and interaction.
 */
export const RadioButtonWithImage = ({
  name,
  isChecked,
  icon = undefined,
  label,
  description,
  onChange,
  className,
  disabled = false,
  value,
  dataTestid,
}: RadioButtonWithImageProps): JSX.Element => (
  <label
    className={cn(
      styles.button,
      description === undefined
        ? styles['layout-column']
        : styles['layout-row'],
      {
        [styles['is-selected']]: isChecked,
        [styles['is-disabled']]: disabled,
      },
      className
    )}
  >
    <div className={styles['button-radio-icon']}>
      {isChecked ? <RadioButtonCheckedSVG /> : <RadioButtonUncheckedSVG />}
    </div>

    {icon && <SvgIcon src={icon} className={styles['button-icon']} alt="" />}

    <input
      checked={isChecked}
      className={styles['visually-hidden']}
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
      data-testid={dataTestid}
    />

    <span className={styles['button-text']}>
      <span>{label}</span>
      {description !== undefined && (
        <span className={styles['button-description']}>{description}</span>
      )}
    </span>
  </label>
)
