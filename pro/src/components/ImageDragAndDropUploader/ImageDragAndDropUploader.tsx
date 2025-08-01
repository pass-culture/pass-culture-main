import cn from 'classnames'
import { useRef, useState, useEffect } from 'react'

import { useNotification } from 'commons/hooks/useNotification'
import { usePrevious } from 'commons/hooks/usePrevious'
import {
  UploadImageValues,
  UploaderModeEnum,
} from 'commons/utils/imageUploadTypes'
import { ImageDragAndDrop } from 'components/ImageDragAndDrop/ImageDragAndDrop'
import {
  ModalImageUpsertOrEdit,
  OnImageUploadArgs,
} from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { ImagePlaceholder } from 'components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from 'components/SafeImage/SafeImage'
import fullEditIcon from 'icons/full-edit.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
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
  const inputDragAndDropRef = useRef<HTMLInputElement>(null)

  const { croppedImageUrl, originalImageUrl } = initialValues
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  const [draftImage, setDraftImage] = useState<File | undefined>(undefined)
  const previousDraftImage = usePrevious(draftImage)

  const [refToFocusOnClose, setRefToFocusOnClose] = useState<
    React.RefObject<HTMLElement> | undefined
  >(inputDragAndDropRef)

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
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    setRefToFocusOnClose(inputDragAndDropRef)
    onImageDelete()
    notify.success('L’image a bien été supprimée')
  }

  const onImageUploadHandler = (values: OnImageUploadArgs) => {
    setIsModalImageOpen(false)
    setDraftImage(values.imageFile)
    setRefToFocusOnClose(updateImageRef)
    onImageUpload(values)
    notify.success('Votre image a bien été importée')
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
        <ModalImageUpsertOrEdit
          mode={mode}
          onImageUpload={onImageUploadHandler}
          onImageDelete={onImageDeleteHandler}
          initialValues={{
            draftImage,
            ...initialValues,
          }}
          onOpenChange={setIsModalImageOpen}
          open={isModalImageOpen}
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
          refToFocusOnClose={refToFocusOnClose}
        />
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
