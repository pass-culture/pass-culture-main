import React, { PureComponent, Fragment } from 'react'
import classnames from 'classnames'
import PropTypes from 'prop-types'

class SubmitAndCancelControl extends PureComponent {
  handleOnClick = (form, query, stockId) => () => {
    form.reset()
    query.changeToReadOnly(null, { id: stockId, key: 'stock' })
  }

  render() {
    const { canSubmit, form, handleSubmit, isRequestPending, query, stockId } = this.props

    return (
      <Fragment>
        <td>
          <button
            className={classnames('button is-primary is-small submitStep', {
              'is-loading': isRequestPending,
            })}
            disabled={!canSubmit}
            onClick={handleSubmit}
            type="submit"
          >
            {'Valider'}
          </button>
        </td>
        <td className="is-clipped">
          <button
            className="button is-secondary is-small cancel-step"
            onClick={this.handleOnClick(form, query, stockId)}
            type="reset"
          >
            {'Annuler'}
          </button>
        </td>
      </Fragment>
    )
  }
}

SubmitAndCancelControl.defaultProps = {
  canSubmit: false,
  stockId: null,
}

SubmitAndCancelControl.propTypes = {
  canSubmit: PropTypes.bool,
  form: PropTypes.shape().isRequired,
  handleSubmit: PropTypes.func.isRequired,
  isRequestPending: PropTypes.bool.isRequired,
  query: PropTypes.shape().isRequired,
  stockId: PropTypes.string,
}

export default SubmitAndCancelControl
