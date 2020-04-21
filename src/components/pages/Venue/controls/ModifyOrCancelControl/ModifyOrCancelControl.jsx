import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { NavLink } from 'react-router-dom'

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
          <NavLink
            className="button is-secondary is-medium"
            id="modify-venue"
            to={`/structures/${offererId}/lieux/${venueId}?modification`}
          >
            {'Modifier le lieu'}
          </NavLink>
        ) : (
          <button
            className="button is-secondary is-medium"
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
  venueId: null,
  isCreatedEntity: false,
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
