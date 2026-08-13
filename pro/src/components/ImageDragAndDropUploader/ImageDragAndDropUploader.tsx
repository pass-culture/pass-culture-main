import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'

import { usePrevious } from '@/commons/hooks/usePrevious'
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
}: ImageDragAndDropUploaderProps) => {
  const snackBar = useSnackBar()
  const updateImageRef = useRef<HTMLButtonElement>(null)
  const inputDragAndDropRef = useRef<HTMLInputElement>(null)

  const { croppedImageUrl, originalImageUrl, credit } = initialValues
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  const [isDeleteImageOpen, setIsDeleteImageOpen] = useState(false)
  const [draftImage, setDraftImage] = useState<File | undefined>(undefined)
  const [draftCredit, setDraftCredit] = useState<string | undefined>(credit)
  const [dragDropResetKey, setDragDropResetKey] = useState(0)
  const previousDraftImage = usePrevious(draftImage)

  const imageUrl = croppedImageUrl || originalImageUrl
  const hasImage = !!imageUrl
  const shouldDisplayActions = hasImage && !hideActionButtons

  useEffect(() => {
    // This is to manage the focus when ImageDragAndDropUploader is re-rendered
    // after an image deletion (after a button action click, not as a result
    // of a deletion from the modal options)
    if (previousDraftImage && !draftImage) {
      inputDragAndDropRef.current?.focus()
    }
  }, [draftImage, previousDraftImage])

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
    snackBar.success('L’image a bien été supprimée')
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
      snackBar.success(successMessage)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de l'importation de votre image"
      )
    }
  }

  return (
    <div className={cn(styles['image-uploader-image-container'], className)}>
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
        />
      )}
      <div
        className={cn(styles['image-uploader-actions-container'], {
          [styles['image-uploader-actions-visible']]: shouldDisplayActions,
        })}
      >
        {shouldDisplayActions && (
          <Button
            ref={updateImageRef}
            onClick={() => setIsModalImageOpen(true)}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            aria-label="Modifier l’image"
            icon={fullEditIcon}
            label="Modifier"
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
          onOpenChange={(open) => {
            if (!open) {
              setDraftImage(undefined)
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
          key={dragDropResetKey}
          ref={inputDragAndDropRef}
          className={dragAndDropClassName}
          onDropOrSelected={(draftImage) => {
            onImageDropOrSelected?.()
            setDraftImage(draftImage)
            setIsModalImageOpen(true)
          }}
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
        actionButtons={
          <>
            <Button
              onClick={() => setIsDeleteImageOpen(false)}
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              label="Annuler"
            />
            <Button
              onClick={onImageDeleteHandler}
              color={ButtonColor.DANGER}
              label="Supprimer l'image"
            />
          </>
        }
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
