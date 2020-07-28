import * as PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../../layout/Icon/Icon'
import EligibleSoon from './EligibleSoon'

export const DepartmentEligibleSoon = ({ birthDate, postalCode }) => (
  <EligibleSoon
    birthDate={birthDate}
    body="Entre ton adresse e-mail : nous te contacterons dès que le pass arrivera dans ton département"
    postalCode={postalCode}
    title="Bientôt disponible dans ton département !"
    visual={<Icon svg="ineligible-department" />}
  />
)

DepartmentEligibleSoon.propTypes = {
  birthDate: PropTypes.string.isRequired,
  postalCode: PropTypes.string.isRequired,
}
