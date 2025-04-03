import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'
import { useState } from 'react'
import { ValidationError } from 'yup'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { ConstraintCheck } from 'components/ConstraintCheck/ConstraintCheck'
import {
  Constraint,
  imageConstraints,
} from 'components/ConstraintCheck/imageConstraints'
import fullEditIcon from 'icons/full-edit.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { BaseFileInput } from 'ui-kit/form/shared/BaseFileInput/BaseFileInput'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { UploaderModeEnum } from '../../types'

import style from './ButtonImageEdit.module.scss'
import { modeValidationConstraints } from './constants'
import {
  ModalImageEdit,
  OnImageUploadArgs,
} from './ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from './types'
import { getValidationSchema } from './validationSchema'

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
  const { logEvent } = useAnalytics()

  const [errors, setErrors] = useState<string[]>([])
  const validationConstraints = modeValidationConstraints[mode]
  const constraintCheckId = 'constraint-check'

  const constraints: Constraint[] = [
    imageConstraints.formats(validationConstraints.types),
    imageConstraints.size(validationConstraints.maxSize),
    imageConstraints.width(validationConstraints.minWidth),
    imageConstraints.height(validationConstraints.minHeight),
  ]

  const validationSchema = getValidationSchema({ constraints })

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

  function onImageSave(values: OnImageUploadArgs) {
    onImageUpload(values)
    setIsModalImageOpen(false)
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const onImageUploadHandler = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newFile: File | null =
      event.currentTarget.files && event.currentTarget.files.length > 0
        ? event.currentTarget.files[0]
        : null

    if (newFile) {
      try {
        await validationSchema.validate(
          { image: newFile },
          { abortEarly: false }
        )

        setImageFile(newFile)

        setIsModalImageOpen(true)
        logEvent(Events.CLICKED_ADD_IMAGE, {
          imageCreationStage: 'import image',
        })
      } catch (validationErrors) {
        setErrors(
          (validationErrors as ValidationError).inner.map(
            (error) => error.path || 'unknown'
          )
        )
        setIsModalImageOpen(false)
      }
    }
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
            <div>
              <BaseFileInput
                isDisabled={false}
                label={''}
                fileTypes={['image/png', 'image/jpeg']}
                isValid={errors.length === 0}
                onChange={onImageUploadHandler}
                ariaDescribedBy={`${constraintCheckId}`}
              >
                <div
                  className={cn(style['button-image-add'], {
                    [style['add-image-venue']]: mode === UploaderModeEnum.VENUE,
                    [style['add-image-offer']]:
                      mode === UploaderModeEnum.OFFER ||
                      mode === UploaderModeEnum.OFFER_COLLECTIVE,
                  })}
                >
                  <SvgIcon
                    src={fullMoreIcon}
                    alt=""
                    className={style['icon']}
                  />
                  <span className={style['label']}>Ajouter une image</span>
                </div>
              </BaseFileInput>
              <ConstraintCheck
                id={constraintCheckId}
                constraints={constraints}
                failingConstraints={errors}
              />
            </div>
          )
        }
      >
        <Dialog.Title asChild>
          <h1 className={style['modal-image-header']}>Modifier une image</h1>
        </Dialog.Title>
        <ModalImageEdit
          mode={mode}
          onImageSave={onImageSave}
          onReplaceImage={onImageUploadHandler}
          onImageDelete={handleImageDelete}
          initialValues={initialValues}
          imageFile={imageFile}
        />
      </DialogBuilder>
    </>
  )
}
