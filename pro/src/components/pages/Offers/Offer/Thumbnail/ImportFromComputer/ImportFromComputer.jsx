/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import Icon from 'components/layout/Icon'
import {
  IMAGE_TYPE,
  MAX_IMAGE_SIZE,
  MIN_IMAGE_HEIGHT,
  MIN_IMAGE_WIDTH,
} from 'components/pages/Offers/Offer/Thumbnail/_constants'
import { imageConstraints } from 'new_components/ConstraintCheck/imageConstraints'
import { useCheckAndSetImage } from 'new_components/ConstraintCheck/useCheckAndSetImage'
import { PreferredOrientation } from 'new_components/PreferredOrientation/PreferredOrientation'

const constraints = [
  imageConstraints.portrait(),
  imageConstraints.formats(IMAGE_TYPE),
  imageConstraints.size(MAX_IMAGE_SIZE),
  imageConstraints.width(MIN_IMAGE_WIDTH),
  imageConstraints.height(MIN_IMAGE_HEIGHT),
]

const ImportFromComputer = ({ setStep, setThumbnail, step }) => {
  const onSetImage = useCallback(
    file => {
      setThumbnail(file)
      setStep(step + 1)
    },
    [setThumbnail, setStep, step]
  )
  const { errors, checkAndSetImage } = useCheckAndSetImage({
    constraints,
    onSetImage,
  })

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
          onChange={checkAndSetImage}
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
