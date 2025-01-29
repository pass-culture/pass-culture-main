import cn from 'classnames'
import { useState } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { UploaderModeEnum } from '../../types'

import style from './ButtonImageEdit.module.scss'
import {
  ModalImageEdit,
  OnImageUploadArgs,
} from './ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from './types'
import { ModalImageUploadBrowser } from './ModalImageEdit/components/ModalImageUploadBrowser/ModalImageUploadBrowser'
import { ImageUploadBrowserFormValues } from './ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/types'

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
  const [image, setImage] = useState<File | undefined>()

  const [isModalImageOpen, setIsModalImageOpen] = useState(false)

  const handleImageDelete = () => {
    onImageDelete()
  }

  function onImageUploadHandler(values: OnImageUploadArgs) {
    onImageUpload(values)
    setIsModalImageOpen(true)
  }

  const onImageClientUpload = (values: ImageUploadBrowserFormValues) => {
    console.log(values)
    setImage(values.image || undefined)
    setIsModalImageOpen(true)
  }
  console.log(initialValues)
  return (
    <>
      <DialogBuilder onOpenChange={setIsModalImageOpen} open={isModalImageOpen}>
        <ModalImageEdit
          mode={UploaderModeEnum.OFFER}
          onImageUpload={onImageUploadHandler}
          onImageDelete={handleImageDelete}
          initialValues={{
            imageUrl,
            originalImageUrl,
          }}
          imageFile={image}
        />
      </DialogBuilder>
      <ModalImageUploadBrowser
        onImageClientUpload={onImageClientUpload}
        mode={mode}
      />
    </>
  )
}
