import cn from 'classnames'
import { useEffect, useId, useRef, useState } from 'react'

import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  UploaderModeEnum,
  type UploadImageValues,
} from '@/commons/utils/imageUploadTypes'
import { ImageDragAndDrop } from '@/components/ImageDragAndDrop/ImageDragAndDrop'
import {
  ModalImageUpsertOrEdit,
  type OnImageUploadArgs,
} from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import fullEditIcon from '@/icons/full-edit.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeWarningIcon from '@/icons/stroke-warning.svg'

import styles from './ImageDragAndDropUploader.module.scss'

export interface ImageDragAndDropUploaderProps {
  className?: string
  dragAndDropClassName?: string
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  warnBeforeDeleting?: boolean
  initialValues?: UploadImageValues
  mode: UploaderModeEnum
  onImageDropOrSelected?: () => void
  hideActionButtons?: boolean
  disabled?: boolean
  /**
   * Element to give focus back to after a snackbar triggered from this component closes.
   * Use this when `hideActionButtons` is true and a parent renders its own trigger button,
   * since the internal edit/import buttons (the default focus targets) are never rendered.
   */
  focusTargetId?: string
  /**
   * Overrides the id of the internal import dropzone. Use this when a parent needs to
   * target it directly (e.g. to restore focus there once an image it deleted elsewhere
   * has been removed and this dropzone becomes the only remaining focusable element).
   */
  importInputId?: string
}

export const ImageDragAndDropUploader = ({
  className,
  dragAndDropClassName,
  onImageUpload,
  onImageDelete,
  warnBeforeDeleting = false,
  initialValues = {},
  mode,
  onImageDropOrSelected,
  hideActionButtons = false,
  disabled = false,
  focusTargetId,
  importInputId,
}: ImageDragAndDropUploaderProps) => {
  const snackBar = useSnackBar()
  const editButtonId = useId()
  const generatedImportButtonId = useId()
  const importButtonId = importInputId ?? generatedImportButtonId
  const editButtonRef = useRef<HTMLButtonElement>(null)
  const importButtonRef = useRef<HTMLInputElement>(null)

  const { croppedImageUrl, originalImageUrl, credit } = initialValues
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  const [isDeleteImageOpen, setIsDeleteImageOpen] = useState(false)
  const [draftImage, setDraftImage] = useState<File | undefined>(undefined)
  const [draftCredit, setDraftCredit] = useState<string | undefined>(credit)
  const [dragDropResetKey, setDragDropResetKey] = useState(0)

  const imageUrl = croppedImageUrl || originalImageUrl
  const hasImage = !!imageUrl
  const shouldDisplayActions = hasImage && !hideActionButtons

  useEffect(() => {
    setDraftCredit(credit)
  }, [credit])

  const onImageDeleteHandler = () => {
    if (warnBeforeDeleting && !isDeleteImageOpen) {
      setIsDeleteImageOpen(true)
      return
    }
    setIsDeleteImageOpen(false)
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    setDraftCredit(undefined)
    onImageDelete()
    snackBar.success(
      'L’image a bien été supprimée',
      focusTargetId ?? importButtonId
    )
  }

  const onImageUploadHandler = async (
    values: OnImageUploadArgs,
    successMessage: string
  ) => {
    setIsModalImageOpen(false)
    setDraftImage(values.imageFile)
    setDraftCredit(values.credit ?? '')
    try {
      await Promise.resolve(onImageUpload(values))
      snackBar.success(successMessage, focusTargetId ?? editButtonId)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de l'importation de votre image",
        focusTargetId ?? importButtonId
      )
    }
  }

  return (
    <div
      className={cn(styles['image-uploader-image-container'], className)}
      tabIndex={-1}
    >
      {hasImage && (
        <SafeImage
          alt="Prévisualisation de l’image"
          testId="image-preview"
          className={cn(styles['image-preview'], {
            [styles['preview-venue']]: mode === UploaderModeEnum.VENUE,
            [styles['preview-offer']]:
              mode === UploaderModeEnum.OFFER ||
              mode === UploaderModeEnum.OFFER_COLLECTIVE,
          })}
          src={imageUrl}
          placeholder={
            <ImagePlaceholder
              className={cn({
                [styles['placeholder-venue']]: mode === UploaderModeEnum.VENUE,
                [styles['placeholder-offer']]:
                  mode === UploaderModeEnum.OFFER ||
                  mode === UploaderModeEnum.OFFER_COLLECTIVE,
              })}
            />
          }
          credit={draftCredit}
        />
      )}
      <div
        className={cn(styles['image-uploader-actions-container'], {
          [styles['image-uploader-actions-visible']]: shouldDisplayActions,
        })}
      >
        {shouldDisplayActions && (
          <Button
            ref={editButtonRef}
            onClick={() => setIsModalImageOpen(true)}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            aria-label="Modifier l’image"
            icon={fullEditIcon}
            label="Modifier"
            id={editButtonId}
          />
        )}
        <ModalImageUpsertOrEdit
          mode={mode}
          onImageUpload={onImageUploadHandler}
          onImageDelete={onImageDeleteHandler}
          initialValues={{
            ...initialValues,
            draftImage,
            credit: draftCredit,
          }}
          refToFocusOnClose={hasImage ? editButtonRef : importButtonRef}
          onOpenChange={(open) => {
            if (!open) {
              setDragDropResetKey((prev) => prev + 1)
            }
            setIsModalImageOpen(open)
          }}
          open={isModalImageOpen}
        />
        {shouldDisplayActions && (
          <Button
            onClick={onImageDeleteHandler}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            icon={fullTrashIcon}
            label="Supprimer"
          />
        )}
      </div>
      {!hasImage && (
        <ImageDragAndDrop
          ref={importButtonRef}
          key={dragDropResetKey}
          className={dragAndDropClassName}
          onDropOrSelected={(draftImage) => {
            onImageDropOrSelected?.()
            setDraftImage(draftImage)
            setIsModalImageOpen(true)
          }}
          id={importButtonId}
          disabled={disabled}
          {...(mode === UploaderModeEnum.OFFER_COLLECTIVE
            ? {
                minSizes: {
                  width: 400,
                  height: 600,
                },
              }
            : {})}
        />
      )}
      <SimpleModal
        title="Votre offre ne sera plus à la une"
        iconPath={strokeWarningIcon}
        isOpen={isDeleteImageOpen}
        onClose={() => setIsDeleteImageOpen(false)}
        actionButtons={[
          <Button
            onClick={() => setIsDeleteImageOpen(false)}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
            key="cancel"
          />,
          <Button
            onClick={onImageDeleteHandler}
            color={ButtonColor.DANGER}
            label="Supprimer l'image"
            key="confirm"
          />,
        ]}
      >
        <p>
          Sans image d'illustration, cette offre ne pourra plus être mise à la
          une de votre catalogue.
        </p>
        <p>Souhaitez-vous réellement supprimer cette image ?</p>
      </SimpleModal>
    </div>
  )
}
