import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import { withFrenchQueryRouter } from 'components/hocs'

const SubmitAndCancelControl = ({
  canSubmit,
  form,
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
        disabled={!canSubmit}
        onClick={handleSubmit}
        type="submit">
        Valider
      </button>
    </td>
    <td className="is-clipped">
      <button
        className="button is-secondary is-small cancel-step"
        onClick={() => {
          form.reset()
          query.changeToReadOnly(null, { id: stockId, key: 'stock' })
        }}>
        Annuler
      </button>
    </td>
  </Fragment>
)

SubmitAndCancelControl.defaultProps = {
  canSubmit: false,
  stockId: null,
}

SubmitAndCancelControl.propTypes = {
  canSubmit: PropTypes.bool,
  form: PropTypes.object.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  isRequestPending: PropTypes.bool.isRequired,
  query: PropTypes.object.isRequired,
  stockId: PropTypes.string,
}

export default withFrenchQueryRouter(SubmitAndCancelControl)
