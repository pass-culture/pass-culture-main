import React from 'react'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'

const HistoryBackButton = ({ history }) => (
  <button
    type="button"
    style={{ left: 0 }}
    onClick={history.goBack}
    className="is-absolute is-white no-border no-background no-outline ml12"
  >
    <span aria-hidden className="icon-previous" title="" />
  </button>
)

HistoryBackButton.propTypes = {
  history: PropTypes.object.isRequired,
}

export default withRouter(HistoryBackButton)
