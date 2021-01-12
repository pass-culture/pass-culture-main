import React, { useCallback, useRef, useState } from 'react'

import { IMAGE_TYPE } from 'components/pages/Offer/Offer/Thumbnail/_constants'
import { ReactComponent as ThumbnailSampleIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/thumbnail-sample.svg'

import Icon from '../../../../../layout/Icon'
import { constraints } from '../_error_validator'

const ImportFromComputer = () => {
  const [error, setError] = useState('')
  const file = useRef(null)

  const getError = async file => {
    for (const constraint of constraints) {
      if (await constraint.validator(file)) return Promise.resolve(constraint.id)
    }
    return Promise.resolve('')
  }

  const isThereAnError = useCallback(async () => {
    const currentFile = file.current.files[0]
    const error = await getError(currentFile)

    setError(error)
  }, [file])

  const fileConstraint = () =>
    constraints.map(constraint => {
      let description = constraint.description

      if (error === constraint.id) {
        description = (
          <strong
            aria-live="assertive"
            aria-relevant="all"
          >
            <Icon svg="ico-notification-error-red" />
            {description}
          </strong>
        )
      }

      return (
        <li key={constraint.id}>
          {description}
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
          aria-invalid={error}
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

export default ImportFromComputer
