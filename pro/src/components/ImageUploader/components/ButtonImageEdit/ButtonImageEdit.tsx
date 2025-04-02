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
}: ButtonImageEditProps): JSX.Element => {
  const { imageUrl, originalImageUrl } = initialValues
  const [imageFile, setImageFile] = useState<File | undefined>()

  const [isModalImageOpen, setIsModalImageOpen] = useState(false)

  const onClickButtonImageAdd = () => {
    if (onClickButtonImage) {
      onClickButtonImage()
    }
  }

  const handleImageDelete = () => {
    onImageDelete()
  }

  function onImageUploadHandler(values: OnImageUploadArgs) {
    setImageFile(values.image)
    setIsModalImageOpen(true)
  }

  function onImageRegister(values: OnImageUploadArgs) {
    onImageUpload(values)
    setIsModalImageOpen(false)
  }

  return (
    <>
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
              onSubmit={onImageUploadHandler}
              mode={UploaderModeEnum.OFFER}
              isReady={true}
            />
          )
        }
      >
        <ModalImageEdit
          mode={mode}
          onImageUpload={onImageRegister}
          onImageDelete={handleImageDelete}
          initialValues={initialValues}
          imageFile={imageFile}
        />
      </DialogBuilder>
    </>
  )
}
