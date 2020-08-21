import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'

class ModifyOrCancelControl extends PureComponent {
  handleOnCLick = () => {
    const { isCreatedEntity, form, history, offererId, venueId } = this.props

    form.reset()
    const next = isCreatedEntity
      ? `/structures/${offererId}`
      : `/structures/${offererId}/lieux/${venueId}`
    history.push(next)
  }

  render() {
    const { offererId, venueId, readOnly } = this.props

    return (
      <div className="control">
        {readOnly ? (
          <Link
            className="secondary-button"
            id="modify-venue"
            to={`/structures/${offererId}/lieux/${venueId}?modification`}
          >
            {'Modifier le lieu'}
          </Link>
        ) : (
          <button
            className="secondary-button"
            onClick={this.handleOnCLick}
            type="reset"
          >
            {'Annuler'}
          </button>
        )}
      </div>
    )
  }
}

ModifyOrCancelControl.defaultProps = {
  isCreatedEntity: false,
  venueId: null,
}

ModifyOrCancelControl.propTypes = {
  form: PropTypes.shape().isRequired,
  history: PropTypes.shape().isRequired,
  isCreatedEntity: PropTypes.bool,
  offererId: PropTypes.string.isRequired,
  readOnly: PropTypes.bool.isRequired,
  venueId: PropTypes.string,
}

export default ModifyOrCancelControl
