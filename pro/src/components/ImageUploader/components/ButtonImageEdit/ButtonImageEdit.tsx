import cn from 'classnames'
import { useState } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { UploaderModeEnum } from '../../types'
import {
  ModalImageEdit,
  OnImageUploadArgs,
} from '../ModalImageEdit/ModalImageEdit'

import style from './ButtonImageEdit.module.scss'
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
            <button
              className={cn(style['button-image-add'], {
                [style['add-image-venue']]: mode === UploaderModeEnum.VENUE,
                [style['add-image-offer']]:
                  mode === UploaderModeEnum.OFFER ||
                  mode === UploaderModeEnum.OFFER_COLLECTIVE,
              })}
              onClick={onClickButtonImageAdd}
              type="button"
              disabled={disableForm}
            >
              <>
                <SvgIcon src={fullMoreIcon} alt="" className={style['icon']} />
                <span className={style['label']}>Ajouter une image</span>
              </>
            </button>
          )
        }
      >
        <ModalImageEdit
          mode={mode}
          onImageUpload={onImageUploadHandler}
          onImageDelete={handleImageDelete}
          initialValues={initialValues}
        />
      </DialogBuilder>
    </>
  )
}
