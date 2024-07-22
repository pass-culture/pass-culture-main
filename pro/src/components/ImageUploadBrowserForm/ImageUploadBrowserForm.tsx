import React, { useState } from 'react'
import { ValidationError } from 'yup'

import { ConstraintCheck } from 'components/ConstraintCheck/ConstraintCheck'
import {
  Constraint,
  imageConstraints,
} from 'components/ConstraintCheck/imageConstraints'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { BaseFileInput } from 'ui-kit/form/shared/BaseFileInput/BaseFileInput'

import { modeValidationConstraints } from './constants'
import { ImageUploadBrowserFormValues } from './types'
import { getValidationSchema } from './validationSchema'

interface ImageUploadBrowserFormProps {
  onSubmit: (values: ImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
  children?: never
}

export const ImageUploadBrowserForm = ({
  onSubmit,
  mode,
}: ImageUploadBrowserFormProps): JSX.Element => {
  const [errors, setErrors] = useState<string[]>([])
  const validationConstraints = modeValidationConstraints[mode]

  const constraints: Constraint[] = [
    imageConstraints.formats(validationConstraints.types),
    imageConstraints.size(validationConstraints.maxSize),
    imageConstraints.width(validationConstraints.minWidth),
    imageConstraints.height(validationConstraints.minHeight),
  ]

  const validationSchema = getValidationSchema({ constraints })

  /* istanbul ignore next: DEBT, TO FIX */
  const onChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newFile: File | null =
      event.currentTarget.files && event.currentTarget.files[0]
        ? event.currentTarget.files[0]
        : null

    if (newFile) {
      try {
        await validationSchema.validate(
          { image: newFile },
          { abortEarly: false }
        )
        onSubmit({ image: newFile })
      } catch (validationErrors) {
        setErrors(
          (validationErrors as ValidationError).inner.map(
            (error) => error.path || 'unknown'
          )
        )
      }
    }
  }

  /* istanbul ignore next: DEBT, TO FIX */
  return (
    <form onSubmit={(e) => e.preventDefault()}>
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
