import React, { useState } from 'react'
import { ValidationError } from 'yup'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
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
  isReady: boolean
  children?: React.ReactNode | React.ReactNode[]
}

export const ImageUploadBrowserForm = ({
  onSubmit,
  mode,
  isReady,
  children,
}: ImageUploadBrowserFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const [errors, setErrors] = useState<string[]>([])
  const validationConstraints = modeValidationConstraints[mode]
  const preferredOrientationCaptionId = 'preferred-orientation-caption'
  const constraintCheckId = 'constraint-check'

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
      event.currentTarget.files && event.currentTarget.files.length > 0
        ? event.currentTarget.files[0]
        : null

    if (newFile) {
      try {
        await validationSchema.validate(
          { image: newFile },
          { abortEarly: false }
        )
        onSubmit({ imageFile: newFile })
        logEvent(Events.CLICKED_ADD_IMAGE, {
          imageCreationStage: 'import image',
        })
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
    <div>
      <BaseFileInput
        isDisabled={!isReady}
        label={''}
        fileTypes={['image/png', 'image/jpeg']}
        isValid={errors.length === 0}
        onChange={onChange}
        ariaDescribedBy={`${preferredOrientationCaptionId} ${constraintCheckId}`}
      >
        {children}
      </BaseFileInput>
      <ConstraintCheck
        id={constraintCheckId}
        constraints={constraints}
        failingConstraints={errors}
      />
    </div>
  )
}
