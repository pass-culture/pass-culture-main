import cn from 'classnames'
import { useRef, useState } from 'react'

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
  id: string
}

export const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
  onImageDelete,
  onClickButtonImage,
  label,
  disableForm,
  id,
}: ButtonImageEditProps): JSX.Element => {
  const { croppedImageUrl, originalImageUrl } = initialValues
  const imageUrl = croppedImageUrl || originalImageUrl
  const snackBar = useSnackBar()

  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  // Explicit target for the modal's close-focus-restore, since the trigger
  // button switches between the "add" and "edit" DOM nodes depending on state.
  const triggerButtonRef = useRef<HTMLButtonElement>(null)

  const onClickButtonImageAdd = () => {
    if (onClickButtonImage) {
      onClickButtonImage()
    }
  }

  async function onImageUploadHandler(
    values: OnImageUploadArgs,
    successMessage: string
  ) {
    setIsModalImageOpen(false)
    try {
      await Promise.resolve(onImageUpload(values))
      snackBar.success(successMessage, id)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de l'importation de votre image",
        id
      )
    }
  }

  return (
    <>
      {imageUrl ? (
        <Button
          ref={triggerButtonRef}
          onClick={() => {
            onClickButtonImageAdd()
            setIsModalImageOpen(true)
          }}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          aria-label="Modifier l’image"
          icon={fullEditIcon}
          label={label ?? 'Modifier'}
          id={id}
        />
      ) : (
        <button
          ref={triggerButtonRef}
          className={cn(style['button-image-add'], {
            [style['add-image-venue']]: mode === UploaderModeEnum.VENUE,
            [style['add-image-offer']]:
              mode === UploaderModeEnum.OFFER ||
              mode === UploaderModeEnum.OFFER_COLLECTIVE,
          })}
          onClick={() => {
            onClickButtonImageAdd()
            setIsModalImageOpen(true)
          }}
          type="button"
          disabled={disableForm}
          id={id}
        >
          <SvgIcon src={fullMoreIcon} alt="" className={style['icon']} />
          <p className={style['label']}>Ajouter une image</p>
        </button>
      )}
      <ModalImageUpsertOrEdit
        mode={mode}
        onImageUpload={onImageUploadHandler}
        onImageDelete={onImageDelete}
        initialValues={initialValues}
        onOpenChange={setIsModalImageOpen}
        open={isModalImageOpen}
        refToFocusOnClose={triggerButtonRef}
      />
    </>
  )
}
