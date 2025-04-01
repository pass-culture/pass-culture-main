import { useState } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { UploaderModeEnum } from '../../types'

import { ImageUploadBrowserForm } from './ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/ImageUploadBrowserForm'
import {
  ModalImageEdit,
  OnImageUploadArgs,
} from './ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from './types'

export type ButtonImageEditProps = {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  initialValues?: UploadImageValues
  mode: UploaderModeEnum
  onClickButtonImage?: () => void
  children?: React.ReactNode
  disableForm?: boolean
}

export const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
  onImageDelete,
  onClickButtonImage,
  children,
  disableForm,
}: ButtonImageEditProps): JSX.Element => {
  const { imageUrl, originalImageUrl } = initialValues
  const [image, setImage] = useState<File>()

  console.log(imageUrl, originalImageUrl)
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)

  const onClickButtonImageAdd = () => {
    if (onClickButtonImage) {
      setIsModalImageOpen(true)
      onClickButtonImage()
    }
  }

  const handleImageDelete = () => {
    onImageDelete()
  }

  const onImageClientUpload = (values: OnImageUploadArgs) => {
    console.log(values)
    setImage(values.image)
    onImageUpload(values)
    setIsModalImageOpen(true)
  }

  return (
    <DialogBuilder
      onOpenChange={setIsModalImageOpen}
      open={isModalImageOpen}
      variant="drawer"
      trigger={
        imageUrl || originalImageUrl ? (
          <Button
            onClick={onClickButtonImageAdd}
            variant={ButtonVariant.TERNARY}
            aria-label="Modifier l’image"
            icon={fullEditIcon}
          >
            {children ?? 'Modifier'}
          </Button>
        ) : (
          <ImageUploadBrowserForm
            label="Ajouter une image"
            isReady={true}
            onSubmit={onImageClientUpload}
            mode={mode}
          />
        )
      }
    >
      <ModalImageEdit
        mode={mode}
        uploadedFile={image}
        onImageUpload={onImageClientUpload}
        onImageDelete={handleImageDelete}
        initialValues={initialValues}
      />
    </DialogBuilder>
  )
}
