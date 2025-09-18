import classNames from 'classnames'
import fullErrorIcon from 'icons/full-error.svg'

import { FiledCharactersCount } from '@/design-system/common/FieldFooter/FiledCharactersCount/FiledCharactersCount'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './FieldFooter.module.scss'

type FieldFooterProps = {
  error?: string
  errorId?: string
  charactersCount?: {
    current: number
    max: number
  }
  charactersCountId?: string
}

export function FieldFooter({
  error,
  errorId,
  charactersCount,
  charactersCountId,
}: FieldFooterProps) {
  return (
    <div
      className={classNames(styles['footer'], {
        [styles['has-footer']]: Boolean(error) || Boolean(charactersCount),
      })}
    >
      <div role="alert" className={styles['error']}>
        {error && (
          <p id={errorId} className={styles['error-content']}>
            <SvgIcon
              src={fullErrorIcon}
              alt=""
              className={styles['error-content-icon']}
            />
            {error}
          </p>
        )}
      </div>
      {charactersCount && charactersCountId && (
        <FiledCharactersCount
          {...charactersCount}
          describeById={charactersCountId}
        />
      )}
    </div>
  )
}
