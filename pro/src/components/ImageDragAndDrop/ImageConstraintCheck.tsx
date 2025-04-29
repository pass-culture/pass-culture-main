import styles from './ImageDragAndDrop.module.scss'

export const ImageConstraintCheck = ({
  label,
  constraint,
  hasError,
  errorMessage,
}: {
  label: string
  constraint: string
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

  return hasError ? (
    <span className={styles['image-drag-and-drop-description-error']}>
      <span className={styles['visually-hidden']}>{errorMessage}</span>
      {imageConstraint}
    </span>
  ) : (
    <span>{imageConstraint}</span>
  )
}
