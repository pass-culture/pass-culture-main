import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

export const BicIbanFields = ({ iban, bic }) => (
  <Fragment>
    <p className="bi-subtitle">
      {
        'Les remboursements des offres éligibles présentées dans ce lieu sont effectués sur le compte ci-dessous :'
      }
    </p>
    <div className="vp-detail">
      <span>
        {'IBAN : '}
      </span>
      <span>
        {iban}
      </span>
    </div>
    <div className="vp-detail">
      <span>
        {'BIC : '}
      </span>
      <span>
        {bic}
      </span>
    </div>
  </Fragment>
)

BicIbanFields.propTypes = {
  bic: PropTypes.string.isRequired,
  iban: PropTypes.string.isRequired,
}
