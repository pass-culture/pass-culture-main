import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'

import PropTypes from 'prop-types'
import React from 'react'

export const STEP_ID_INFORMATIONS = 'informations'
export const STEP_ID_MANAGEMENT = 'management'
export const mapPathToStep = {
  informations: STEP_ID_INFORMATIONS,
  gestion: STEP_ID_MANAGEMENT,
}

const VenueBreadcrumb = ({ activeStep, offererId, venueId }) => {
  const isCreatingVenue = venueId === null
  let baseUrl = `/structures/${offererId}/lieux/`
  baseUrl += isCreatingVenue ? 'creation/' : `${venueId}/`

  const steps = [
    {
      id: STEP_ID_INFORMATIONS,
      label: 'Informations',
      url: `${baseUrl}informations`,
    },
    {
      id: STEP_ID_MANAGEMENT,
      label: 'Gestions',
      url: `${baseUrl}gestion`,
    },
  ]

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={steps}
      styleType={
        isCreatingVenue ? BreadcrumbStyle.DEFAULT : BreadcrumbStyle.TAB
      }
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
