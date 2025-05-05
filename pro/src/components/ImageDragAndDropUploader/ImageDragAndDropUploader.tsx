import cn from 'classnames'
import { useRef, useState } from 'react'

import { useNotification } from 'commons/hooks/useNotification'
import {
  UploadImageValues,
  UploaderModeEnum,
} from 'commons/utils/imageUploadTypes'
import { ImageDragAndDrop } from 'components/ImageDragAndDrop/ImageDragAndDrop'
import {
  ModalImageUpsertOrEdit,
  OnImageUploadArgs,
} from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import fullEditIcon from 'icons/full-edit.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ImageDragAndDropUploader.module.scss'

export interface ImageDragAndDropUploaderProps {
  className?: string
  dragAndDropClassName?: string
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
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
  initialValues = {},
  mode,
  onImageDropOrSelected,
  hideActionButtons = false,
  disabled = false,
}: ImageDragAndDropUploaderProps) => {
  const notify = useNotification()
  const updateImageRef = useRef<HTMLButtonElement>(null)
  const { imageUrl, originalImageUrl } = initialValues
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  const [draftImage, setDraftImage] = useState<File | undefined>(undefined)

  const hasImage = imageUrl && originalImageUrl
  const shouldDisplayActions = hasImage && !hideActionButtons

  const onImageDeleteHandler = () => {
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    onImageDelete()
    notify.success('L’image a bien été supprimée')
  }

  const onImageUploadHandler = (values: OnImageUploadArgs) => {
    setIsModalImageOpen(false)
    setDraftImage(values.imageFile)
    onImageUpload(values)
    notify.success('Votre image a bien été enregistrée')
  }

  return (
    <div className={cn(styles['image-uploader-image-container'], className)}>
      {hasImage && (
        <img
          alt={'Prévisualisation de l’image'}
          data-testid="image-preview"
          className={cn(styles['image-preview'], {
            [styles['preview-venue']]: mode === UploaderModeEnum.VENUE,
            [styles['preview-offer']]:
              mode === UploaderModeEnum.OFFER ||
              mode === UploaderModeEnum.OFFER_COLLECTIVE,
          })}
          src={imageUrl}
        />
      )}
      <div
        className={cn(styles['image-uploader-actions-container'], {
          [styles['image-uploader-actions-visible']]: shouldDisplayActions,
        })}
      >
        <DialogBuilder
          onOpenChange={setIsModalImageOpen}
          open={isModalImageOpen}
          variant="drawer"
          trigger={
            shouldDisplayActions && (
              <Button
                ref={updateImageRef}
                variant={ButtonVariant.TERNARY}
                aria-label="Modifier l’image"
                icon={fullEditIcon}
              >
                Modifier
              </Button>
            )
          }
        >
          <ModalImageUpsertOrEdit
            mode={mode}
            onImageUpload={onImageUploadHandler}
            onImageDelete={onImageDeleteHandler}
            initialValues={{
              draftImage,
              ...initialValues,
            }}
          />
        </DialogBuilder>
        {shouldDisplayActions && (
          <Button
            onClick={onImageDeleteHandler}
            variant={ButtonVariant.TERNARY}
          >
            <SvgIcon
              alt=""
              className={styles['button-image-delete-icon']}
              src={fullTrashIcon}
            />
            Supprimer
          </Button>
        )}
      </div>
      {!hasImage && (
        <ImageDragAndDrop
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
                  width: 600,
                  height: 400,
                },
              }
            : {})}
        />
      )}
    </div>
  )
}
