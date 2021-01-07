import React, { useCallback, useRef, useState } from 'react'

import { IMAGE_TYPE } from 'components/pages/Offer/Offer/Thumbnail/_constants'
import { ReactComponent as ThumbnailSampleIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/thumbnail-sample.svg'

import { constraints } from '../_error_validator'

const ThumbnailFile = () => {
  const [errors, setErrors] = useState([])
  const file = useRef(null)

  const getErrors = async file => {
    const errors = []
    await Promise.all(
      constraints.map(
        async constraint => (await constraint.validator(file)) && errors.push(constraint.id)
      )
    )

    return Promise.resolve(errors)
  }

  const isThereAnError = useCallback(async () => {
    const currentFile = file.current.files[0]
    const errors = await getErrors(currentFile)

    setErrors(errors)
  }, [file])

  const fileConstraint = () =>
    constraints.map(constraint => {
      let sentence = constraint.sentence

      if (errors.length > 0 && errors.includes(constraint.id)) {
        sentence = (
          <strong
            aria-live="assertive"
            aria-relevant="all"
          >
            {sentence}
          </strong>
        )
      }

      return (
        <li key={constraint.id}>
          {sentence}
        </li>
      )
    })

  return (
    <form className="tnf-form">
      <ThumbnailSampleIcon />
      <p className="tnf-info">
        {'Utilisez de préférence un visuel en orientation portrait'}
      </p>
      <label className="tnf-file-label primary-link">
        {'Importer une image depuis l’ordinateur'}
        <input
          accept={IMAGE_TYPE.join()}
          aria-invalid={errors.length > 0 ? true : false}
          className="tnf-file-input"
          onChange={isThereAnError}
          ref={file}
          type="file"
        />
      </label>
      <ul className="tnf-mandatory">
        {fileConstraint()}
      </ul>
    </form>
  )
}

export default ThumbnailFile
