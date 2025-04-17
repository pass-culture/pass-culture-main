import { useId } from 'react'

import styles from './Slider.module.scss'

const DEFAULT_SLIDER_MIN_VALUE = 0
const DEFAULT_SLIDER_MAX_VALUE = 100
const DEFAULT_SLIDER_STEP_VALUE = 1

/**
 * Props for the Slider component.
 *
 * @extends React.HTMLProps<HTMLInputElement>
 */
export interface SliderProps extends React.HTMLProps<HTMLInputElement> {
  /**
   * The name of the slider field.
   */
  name: string
  /**
   * The scale or unit of the value being represented (e.g., '%', 'kg', etc.).
   * @default ''
   */
  scale?: string
  /**
   * Whether to hide the label visually.
   * @default false
   */
  hideLabel?: boolean
  /**
   * Whether to display the minimum and maximum values.
   * @default true
   */
  displayMinMaxValues?: boolean
  /**
   * Whether to display the current value of the slider.
   * @default false
   */
  displayValue?: boolean
  /**
   * The handleChange function's event is typed as React.ChangeEvent<HTMLInputElement>
   */
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
}

/**
 * The Slider component is a customizable input slider that integrates with Formik for form state management.
 * It provides features such as labeling, displaying min/max values, and showing the current slider value.
 *
 * ---
 * **Important: Always provide a label for accessibility.**
 * Labels are crucial for screen readers and users who rely on assistive technology. If the label should not be visible, use `hideLabel` to visually hide it but still make it accessible.
 * ---
 *
 * @param {SliderProps} props - The props for the Slider component.
 * @returns {JSX.Element} The rendered Slider component.
 *
 * @example
 * <Slider
 *   name="volume"
 *   label="Volume Control"
 *   scale="%"
 *   displayValue={true}
 *   displayMinMaxValues={true}
 * />
 *
 * @accessibility
 * - **Labels**: Always provide a meaningful label using the `label` prop or the `fieldName` for screen readers. Use `hideLabel` if the label should be visually hidden but still accessible.
 * - **Keyboard Accessibility**: Ensure that users can adjust the slider value using the keyboard (e.g., arrow keys).
 * - **ARIA Attributes**: The component uses standard `input[type="range"]` elements, ensuring native browser support for screen readers and accessibility tools. If the slider is required, consider adding `aria-required` manually.
 * - **Visual Feedback**: The `displayValue` prop provides instant feedback on the current value, improving usability for all users, including those with cognitive impairments.
 */
export const Slider = ({
  scale = '',
  hideLabel = false,
  displayMinMaxValues = true,
  displayValue = false,
  onChange,
  ...props
}: SliderProps): JSX.Element => {
  const labelId = useId()
  const min = props.min || DEFAULT_SLIDER_MIN_VALUE
  const max = props.max || DEFAULT_SLIDER_MAX_VALUE

  return (
    <div>
      <div className={styles['slider-header']}>
        <label
          htmlFor={labelId}
          className={hideLabel ? styles['visually-hidden'] : ''}
        >
          {props.label}
        </label>
        {displayValue && (
          <span className={styles['input-value']}>
            {props.value}&nbsp;{scale}
          </span>
        )}
      </div>
      <input
        data-testid="slider"
        type="range"
        id={labelId}
        className={styles.slider}
        min={min}
        max={max}
        value={props.value}
        step={props.step || DEFAULT_SLIDER_STEP_VALUE}
        onChange={onChange}
        {...props}
      />
      {displayMinMaxValues && (
        <div className={styles['min-max-container']}>
          <span>
            <span className={styles['visually-hidden']}>Entre </span>
            {`${min} ${scale}`}
          </span>
          <span>
            <span className={styles['visually-hidden']}>et </span>
            {`${max} ${scale}`}
          </span>
        </div>
      )}
    </div>
  )
}
