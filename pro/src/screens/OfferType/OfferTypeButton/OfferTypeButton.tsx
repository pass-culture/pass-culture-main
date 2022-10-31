import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'

import { OFFER_SUBTYPES, OFFER_TYPES } from 'core/Offers'
import { ReactComponent as TickIcon } from 'icons/tick.svg'

import styles from './OfferTypeButton.module.scss'

interface IOfferTypeButton {
  isSelected: boolean
  Icon: FunctionComponent<
    SVGProps<SVGSVGElement> & { title?: string | undefined }
  >
  label: string
  description?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  className?: string
  disabled?: boolean
  value: OFFER_TYPES | OFFER_SUBTYPES
}

const OfferTypeButton = ({
  isSelected,
  Icon,
  label,
  description,
  onChange,
  className,
  disabled = false,
  value,
}: IOfferTypeButton): JSX.Element => (
  <label
    className={cn(
      styles.button,
      description === undefined
        ? styles['layout-column']
        : styles['layout-row'],
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
    <div className={styles['button-text']}>
      <div>{label}</div>
      {description !== undefined && (
        <div className={styles['button-description']}>{description}</div>
      )}
    </div>
  </label>
)

export default OfferTypeButton
