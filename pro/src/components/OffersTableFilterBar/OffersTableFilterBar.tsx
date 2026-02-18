import classNames from 'classnames'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'

import styles from './OffersTableFilterBar.module.scss'

interface OffersTableFilterBarProps {
  children: React.ReactNode
  id?: string
  isDisabled?: boolean
  isHidden?: boolean
  isInline?: boolean
  onReset: () => void
}
export const OffersTableFilterBar = ({
  children,
  id,
  isDisabled = false,
  isHidden = false,
  isInline = false,
  onReset,
}: Readonly<OffersTableFilterBarProps>) => {
  return (
    <div
      className={classNames({ [styles['box-inline']]: isInline })}
      data-testid="offers-filter"
      hidden={isHidden}
      id={id}
    >
      {children}

      <div>
        <Button
          color={ButtonColor.NEUTRAL}
          disabled={isDisabled}
          icon={fullRefreshIcon}
          label="Réinitialiser les filtres"
          onClick={onReset}
          type="button"
          variant={ButtonVariant.TERTIARY}
        />
      </div>
    </div>
  )
}
