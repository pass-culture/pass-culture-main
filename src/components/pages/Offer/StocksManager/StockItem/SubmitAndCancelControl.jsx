import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import { withFrenchQueryRouter } from 'components/hocs'

const SubmitAndCancelControl = ({
  handleSubmit,
  isRequestPending,
  query,
  stockId,
}) => (
  <Fragment>
    <td>
      <button
        className={classnames('button is-primary is-small submitStep', {
          'is-loading': isRequestPending,
        })}
        onClick={handleSubmit}
        type="submit">
        Valider
      </button>
    </td>
    <td className="is-clipped">
      <button
        className="button is-secondary is-small cancel-step"
        onClick={() => query.changeToReadOnlyUrl('stock', stockId)}>
        Annuler
      </button>
    </td>
  </Fragment>
)

SubmitAndCancelControl.defaultProps = {
  stockId: null,
}

SubmitAndCancelControl.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  isRequestPending: PropTypes.bool.isRequired,
  query: PropTypes.object.isRequired,
  stockId: PropTypes.string,
}

export default withFrenchQueryRouter(SubmitAndCancelControl)
