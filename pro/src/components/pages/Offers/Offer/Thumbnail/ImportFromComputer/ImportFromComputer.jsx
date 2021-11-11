/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import * as PropTypes from 'prop-types'
import React, { useCallback, useRef, useState } from 'react'

import Icon from 'components/layout/Icon'
import { IMAGE_TYPE } from 'components/pages/Offers/Offer/Thumbnail/_constants'
import { constraints } from 'components/pages/Offers/Offer/Thumbnail/_error_validator'
import { ReactComponent as ThumbnailSampleIcon } from 'components/pages/Offers/Offer/Thumbnail/assets/thumbnail-sample.svg'

const ImportFromComputer = ({ setStep, setThumbnail, step }) => {
  const [error, setError] = useState('')
  const file = useRef({})

  const getError = async file => {
    for (const constraint of constraints) {
      const inError = constraint.asyncValidator ? await constraint.asyncValidator(file) : constraint.validator(file)
      if (inError) {
        return Promise.resolve(constraint.id)
      }
    }
    return Promise.resolve('')
  }

  const submitThumbnail = useCallback(async () => {
    const currentFile = file.current.files[0]
    const error = await getError(currentFile)
    if (error === '') {
      setThumbnail(currentFile)
      setStep(step + 1)
    }

    setError(error)
  }, [setStep, setThumbnail, step])

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
    <form
      action="#"
      className="tnf-form"
    >
      <ThumbnailSampleIcon />
      <p className="tnf-info">
        Utilisez de préférence un visuel en orientation portrait
      </p>
      <label className="tnf-file-label primary-link">
        Importer une image depuis l’ordinateur
        <input
          accept={IMAGE_TYPE.join()}
          aria-invalid={error}
          className="tnf-file-input"
          onChange={submitThumbnail}
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

ImportFromComputer.propTypes = {
  setStep: PropTypes.func.isRequired,
  setThumbnail: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
}

export default ImportFromComputer
