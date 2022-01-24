/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import * as PropTypes from 'prop-types'
import React, { useCallback, useRef, useState } from 'react'

import Icon from 'components/layout/Icon'
import { IMAGE_TYPE } from 'components/pages/Offers/Offer/Thumbnail/_constants'
import { constraints } from 'components/pages/Offers/Offer/Thumbnail/_error_validator'
import { PreferredOrientation } from 'new_components/PreferredOrientation/PreferredOrientation'

const ImportFromComputer = ({ setStep, setThumbnail, step }) => {
  const [errors, setErrors] = useState([])
  const file = useRef({})

  const getValidatorErrors = async file => {
    let validatorErrors = []
    for (const constraint of constraints) {
      const inError = constraint.asyncValidator
        ? await constraint.asyncValidator(file)
        : constraint.validator(file)
      if (inError) {
        validatorErrors = [...validatorErrors, constraint.id]
      }
    }
    return Promise.resolve(validatorErrors)
  }

  const submitThumbnail = useCallback(async () => {
    const currentFile = file.current.files[0]
    const validatorErrors = await getValidatorErrors(currentFile)
    if (validatorErrors.length === 0) {
      setThumbnail(currentFile)
      setStep(step + 1)
    }
    setErrors(validatorErrors)
  }, [setStep, setThumbnail, step])

  const fileConstraint = () =>
    constraints.map(constraint => {
      let description = constraint.description

      if (errors.includes(constraint.id)) {
        description = (
          <strong aria-live="assertive" aria-relevant="all">
            <Icon svg="ico-notification-error-red" />
            {description}
          </strong>
        )
      }

      return <li key={constraint.id}>{description}</li>
    })

  return (
    <form action="#" className="tnf-form">
      <PreferredOrientation orientation="portrait" />
      <label className="tnf-file-label primary-link">
        Importer une image depuis l’ordinateur
        <input
          accept={IMAGE_TYPE.join()}
          aria-invalid={errors}
          className="tnf-file-input"
          onChange={submitThumbnail}
          ref={file}
          type="file"
        />
      </label>
      <ul className="tnf-mandatory">{fileConstraint()}</ul>
    </form>
  )
}

ImportFromComputer.propTypes = {
  setStep: PropTypes.func.isRequired,
  setThumbnail: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
}

export default ImportFromComputer
