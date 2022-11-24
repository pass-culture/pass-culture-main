import React, { useState } from 'react'
import { ValidationError } from 'yup'

import { ConstraintCheck } from 'components/ConstraintCheck/ConstraintCheck'
import {
  Constraint,
  imageConstraints,
} from 'components/ConstraintCheck/imageConstraints'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { BaseFileInput } from 'ui-kit/form/shared'

import { modeValidationConstraints } from './constants'
import { IImageUploadBrowserFormValues, OrientationEnum } from './types'
import getValidationSchema from './validationSchema'

interface IImageUploadBrowserFormProps {
  onSubmit: (values: IImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
  children?: never
}

const ImageUploadBrowserForm = ({
  onSubmit,
  mode,
}: IImageUploadBrowserFormProps): JSX.Element => {
  const [errors, setErrors] = useState<string[]>([])
  const validationConstraints = modeValidationConstraints[mode]
  const validationMinHeight =
    'minHeight' in validationConstraints
      ? validationConstraints.minHeight
      : undefined
  const orientation: OrientationEnum =
    mode === UploaderModeEnum.VENUE
      ? OrientationEnum.LANDSCAPE
      : OrientationEnum.PORTRAIT

  const constraints: Constraint[] = [
    imageConstraints.formats(validationConstraints.types),
    imageConstraints.size(validationConstraints.maxSize),
    imageConstraints.width(validationConstraints.minWidth),
    imageConstraints.height(validationMinHeight),
    imageConstraints.minRatio(validationConstraints.minRatio, orientation),
  ]

  const validationSchema = getValidationSchema(validationConstraints)

  /* istanbul ignore next: DEBT, TO FIX */
  const onChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newFile: File | null =
      (event.currentTarget.files && event.currentTarget.files[0]) || null
    if (newFile) {
      validationSchema
        .validate({ image: newFile }, { abortEarly: false })
        .then(() => onSubmit({ image: newFile }))
        .catch((validationErrors: ValidationError) =>
          setErrors(
            validationErrors.inner.map(error => error.path || 'unknown')
          )
        )
    }
  }

  /* istanbul ignore next: DEBT, TO FIX */
  return (
    <form onSubmit={e => e.preventDefault()}>
      <BaseFileInput
        label="Importer une image depuis l’ordinateur"
        fileTypes={['image/png', 'image/jpeg']}
        isValid={errors.length === 0}
        onChange={onChange}
      />
      <ConstraintCheck constraints={constraints} failingConstraints={errors} />
    </form>
  )
}

export default ImageUploadBrowserForm
