import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { ConstraintCheck } from 'components/ConstraintCheck/ConstraintCheck'
import { imageConstraints } from 'components/ConstraintCheck/imageConstraints'
import { useCheckAndSetImage } from 'components/ConstraintCheck/useCheckAndSetImage'
import { PreferredOrientation } from 'components/PreferredOrientation/PreferredOrientation'
import {
  IMAGE_TYPE,
  MAX_IMAGE_SIZE,
  MIN_IMAGE_WIDTH,
} from 'pages/Offers/Offer/Thumbnail/_constants'
import { BaseFileInput } from 'ui-kit/form/shared'

const constraints = [
  imageConstraints.formats(IMAGE_TYPE),
  imageConstraints.size(MAX_IMAGE_SIZE),
  imageConstraints.width(MIN_IMAGE_WIDTH),
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
      <BaseFileInput
        label="Importer une image depuis l’ordinateur"
        fileTypes={IMAGE_TYPE}
        isValid={!errors}
        onChange={checkAndSetImage}
      />
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
