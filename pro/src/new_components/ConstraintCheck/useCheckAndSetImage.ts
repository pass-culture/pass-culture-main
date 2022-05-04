import React, { useCallback, useState } from 'react'

import { Constraint, getValidatorErrors } from './imageConstraints'

type UseCheckAndSetImage = (args: {
  constraints: Constraint[]
  onSetImage: (file: string) => void
}) => {
  errors: string[]
  checkAndSetImage: React.ChangeEventHandler<HTMLInputElement>
}

export const useCheckAndSetImage: UseCheckAndSetImage = ({
  constraints,
  onSetImage,
}) => {
  const [errors, setErrors] = useState<string[]>([])

  const checkAndSetImage = useCallback<
    React.ChangeEventHandler<HTMLInputElement>
  >(
    async event => {
      const files = event.target.files

      if (files?.length !== 1) return

      const currentFile = files[0]
      const validatorErrors = await getValidatorErrors(constraints, currentFile)

      if (validatorErrors.length === 0) {
        // FIX ME: don't cast
        onSetImage(currentFile as unknown as string)
      }

      setErrors(validatorErrors)
    },
    [constraints, onSetImage]
  )

  return { errors, checkAndSetImage }
}
