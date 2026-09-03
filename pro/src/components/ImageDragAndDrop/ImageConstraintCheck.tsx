import cn from 'classnames'

import fullClearIcon from '@/icons/full-clear.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ImageDragAndDrop.module.scss'

export const ImageConstraintCheck = ({
  label,
  constraint,
  hasInput,
  hasError,
}: {
  label: string
  constraint: string
  hasInput?: boolean
  hasError: boolean
}) => {
  const imageConstraint = (
    <>
      {`${label} : `}
      <span className={styles['image-drag-and-drop-description-values']}>
        {constraint}
      </span>
    </>
  )

  return (
    <div
      className={cn({
        [styles['image-drag-and-drop-description-error']]: hasError,
        [styles['image-drag-and-drop-description-validate']]: !hasError,
      })}
    >
      {hasInput && (
        <SvgIcon src={hasError ? fullClearIcon : fullValidateIcon} width="16" />
      )}
      <p
        className={cn({
          [styles['image-drag-and-drop-description-neutral']]: !hasInput,
        })}
      >
        {imageConstraint}
      </p>
    </div>
  )
}
