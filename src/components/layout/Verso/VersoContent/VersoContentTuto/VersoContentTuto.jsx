import PropTypes from 'prop-types'
import React from 'react'

const VersoContentTuto = ({ imageURL }) => (
  <div className="verso-info-tuto">
    <img
      alt="verso"
      className="verso-tuto-mediation is-full-width"
      src={imageURL}
    />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
  </div>
)

VersoContentTuto.propTypes = {
  imageURL: PropTypes.string.isRequired,
}

export default VersoContentTuto
