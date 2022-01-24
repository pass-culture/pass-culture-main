/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import {
  IMAGE_TYPE,
  MAX_IMAGE_SIZE,
  MIN_IMAGE_HEIGHT,
  MIN_IMAGE_WIDTH,
} from 'components/pages/Offers/Offer/Thumbnail/_constants'
import { ConstraintCheck } from 'new_components/ConstraintCheck/ConstraintCheck'
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
      <ConstraintCheck constraints={constraints} failingConstraints={errors} />
    </form>
  )
}

ImportFromComputer.propTypes = {
  setStep: PropTypes.func.isRequired,
  setThumbnail: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
}

export default ImportFromComputer
