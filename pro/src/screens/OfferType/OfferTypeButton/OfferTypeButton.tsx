import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'

import { OFFER_TYPES } from 'core/Offers'
import { ReactComponent as TickIcon } from 'icons/tick.svg'

import styles from './OfferTypeButton.module.scss'

interface IOfferTypeButton {
  isSelected: boolean
  Icon: FunctionComponent<
    SVGProps<SVGSVGElement> & { title?: string | undefined }
  >
  label: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  className?: string
  disabled?: boolean
  value: OFFER_TYPES
}

const OfferTypeButton = ({
  isSelected,
  Icon,
  label,
  onChange,
  className,
  disabled = false,
  value,
}: IOfferTypeButton): JSX.Element => (
  <label
    className={cn(
      styles.button,
      {
        [styles['is-selected']]: isSelected,
        [styles['is-disabled']]: disabled,
      },
      className
    )}
  >
    {isSelected ? <TickIcon className={styles['button-check-mark']} /> : null}
    <Icon className={styles['button-icon']} />
    <input
      checked={isSelected}
      className={styles['button-radio']}
      disabled={disabled}
      name="offer-type"
      onChange={onChange}
      type="radio"
      value={value}
    />
    {label}
  </label>
)

export default OfferTypeButton
