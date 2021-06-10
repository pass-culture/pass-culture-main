import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB, STYLE_TYPE_DEFAULT } from 'components/layout/Breadcrumb'

export const STEP_ID_INFORMATIONS = 'informations'
export const STEP_ID_MANAGEMENT = 'management'
export const mapPathToStep = {
  informations: STEP_ID_INFORMATIONS,
  gestion: STEP_ID_MANAGEMENT,
}

const VenueBreadcrumb = ({ activeStep, offererId, venueId }) => {
  const isCreatingVenue = venueId === null
  let baseUrl = `/structures/${offererId}/lieux/`
  baseUrl += isCreatingVenue ? 'creation/' : `${venueId}/edition/`

  const steps = [
    {
      id: STEP_ID_INFORMATIONS,
      label: 'Informations',
      url: `${baseUrl}informations`,
    },
    {
      id: STEP_ID_MANAGEMENT,
      label: 'Gestion',
      url: `${baseUrl}gestion`,
    },
  ]

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={steps}
      styleType={isCreatingVenue ? STYLE_TYPE_DEFAULT : STYLE_TYPE_TAB}
    />
  )
}

VenueBreadcrumb.defaultProps = {
  venueId: null,
}

VenueBreadcrumb.propTypes = {
  activeStep: PropTypes.string.isRequired,
  offererId: PropTypes.string.isRequired,
  venueId: PropTypes.string,
}

export default VenueBreadcrumb
