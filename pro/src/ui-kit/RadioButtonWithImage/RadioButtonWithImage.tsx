import cn from 'classnames'

import { ReactComponent as RadioOffIcon } from 'icons/ico-radio-off.svg'
import { ReactComponent as RadioOnIcon } from 'icons/ico-radio-on.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './RadioButtonWithImage.module.scss'

export interface IRadioButtonWithImage {
  name: string
  isChecked: boolean
  icon: string
  label: string
  description?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  className?: string
  disabled?: boolean
  value: string
  dataTestid?: string
  transparent?: boolean
}

const RadioButtonWithImage = ({
  name,
  isChecked,
  icon,
  label,
  description,
  onChange,
  className,
  disabled = false,
  value,
  dataTestid,
  transparent = false,
}: IRadioButtonWithImage): JSX.Element => (
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
    {isChecked ? (
      <RadioOnIcon className={styles['button-radio-on']} />
    ) : (
      <RadioOffIcon className={styles['button-radio-off']} />
    )}
    <SvgIcon
      src={icon}
      className={cn(
        styles['button-icon'],
        transparent && styles['button-icon-transparent']
      )}
      alt={name + ' - button'}
    />
    <input
      checked={isChecked}
      className={styles['button-radio']}
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
      data-testid={dataTestid}
    />
    <div className={styles['button-text']}>
      <div>{label}</div>
      {description !== undefined && (
        <div className={styles['button-description']}>{description}</div>
      )}
    </div>
  </label>
)

export default RadioButtonWithImage
