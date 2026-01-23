import cn from 'classnames'
import { useState } from 'react'

import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  UploaderModeEnum,
  type UploadImageValues,
} from '@/commons/utils/imageUploadTypes'
import {
  ModalImageUpsertOrEdit,
  type OnImageUploadArgs,
} from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'
import fullMoreIcon from '@/icons/full-more.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import style from './ButtonImageEdit.module.scss'

export type ButtonImageEditProps = {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  initialValues?: UploadImageValues
  mode: UploaderModeEnum
  onClickButtonImage?: () => void
  label?: string
  disableForm?: boolean
}

export const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
  onImageDelete,
  onClickButtonImage,
  label,
  disableForm,
}: ButtonImageEditProps): JSX.Element => {
  const { croppedImageUrl, originalImageUrl } = initialValues
  const imageUrl = croppedImageUrl || originalImageUrl
  const snackBar = useSnackBar()

  const [isModalImageOpen, setIsModalImageOpen] = useState(false)

  const onClickButtonImageAdd = () => {
    if (onClickButtonImage) {
      onClickButtonImage()
    }
  }

  const handleImageDelete = () => {
    onImageDelete()
    snackBar.success('Votre image a bien été supprimée')
  }

  function onImageUploadHandler(
    values: OnImageUploadArgs,
    successMessage: string
  ) {
    onImageUpload(values)
    setIsModalImageOpen(false)
    snackBar.success(successMessage)
  }

  return (
    <ModalImageUpsertOrEdit
      mode={mode}
      onImageUpload={onImageUploadHandler}
      onImageDelete={handleImageDelete}
      initialValues={initialValues}
      onOpenChange={setIsModalImageOpen}
      open={isModalImageOpen}
      trigger={
        imageUrl ? (
          <Button
            onClick={onClickButtonImageAdd}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            aria-label="Modifier l’image"
            icon={fullEditIcon}
            label={label ?? 'Modifier'}
          />
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
            <SvgIcon src={fullMoreIcon} alt="" className={style['icon']} />
            <span className={style['label']}>Ajouter une image</span>
          </button>
        )
      }
    />
  )
}
