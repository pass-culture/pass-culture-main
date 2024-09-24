import cn from 'classnames'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'

import fullEditIcon from 'icons/full-edit.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { UploaderModeEnum } from '../types'

import style from './ButtonImageEdit.module.scss'
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
}

export const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
  onImageDelete,
  onClickButtonImage,
  children,
}: ButtonImageEditProps): JSX.Element => {
  const { t } = useTranslation('common')
  const { imageUrl, originalImageUrl } = initialValues

  const [isModalImageOpen, setIsModalImageOpen] = useState(false)

  const onClickButtonImageAdd = () => {
    onClickButtonImage && onClickButtonImage()
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
            >
              <>
                <SvgIcon
                  src={strokeMoreIcon}
                  alt=""
                  className={style['icon']}
                />
                <span className={style['label']}>{t('add_image')}</span>
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
