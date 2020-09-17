import * as PropTypes from 'prop-types'
import React from 'react'

import { Animation } from '../Animation/Animation'
import EligibleSoon from './EligibleSoon'

export const AgeEligibleSoon = ({ birthDate, postalCode }) => (
  <EligibleSoon
    birthDate={birthDate}
    body="Pour profiter du pass Culture, tu dois avoir 18 ans. Entre ton adresse email : nous t’avertirons dès que tu seras éligible."
    postalCode={postalCode}
    title="C’est pour bientôt !"
    visual={(
      <Animation
        name="ineligible-under-eighteen-animation"
        speed={0.7}
      />
    )}
  />
)

AgeEligibleSoon.propTypes = {
  birthDate: PropTypes.string.isRequired,
  postalCode: PropTypes.string.isRequired,
}
