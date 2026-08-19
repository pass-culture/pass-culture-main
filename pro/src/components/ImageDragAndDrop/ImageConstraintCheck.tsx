import fullClearIcon from '@/icons/full-clear.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ImageDragAndDrop.module.scss'

export const ImageConstraintCheck = ({
  label,
  constraint,
  hasInput,
  hasError,
  errorMessage,
}: {
  label: string
  constraint: string
  hasInput?: boolean
  hasError: boolean
  errorMessage: string
}) => {
  const imageConstraint = (
    <>
      {`${label} : `}
      <span className={styles['image-drag-and-drop-description-values']}>
        {constraint}
      </span>
    </>
  )

  if (!hasInput) {
    return (
      <p className={styles['image-drag-and-drop-description-neutral']}>
        {imageConstraint}
      </p>
    )
  }

  return hasError ? (
    <div className={styles['image-drag-and-drop-description-error']}>
      <SvgIcon src={fullClearIcon} width="16" />
      <span className={styles['visually-hidden']}>{errorMessage}</span>
      <p>{imageConstraint}</p>
    </div>
  ) : (
    <div className={styles['image-drag-and-drop-description-validate']}>
      <SvgIcon src={fullValidateIcon} width="16" />
      <span className={styles['visually-hidden']}>Valide : </span>
      <p>{imageConstraint}</p>
    </div>
  )
}
