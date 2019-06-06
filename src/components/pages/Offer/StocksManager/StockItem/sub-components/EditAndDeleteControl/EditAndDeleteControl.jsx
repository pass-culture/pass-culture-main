import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { Portal } from 'react-portal'
import { requestData } from 'redux-saga-data'

import DeleteDialog from '../DeleteDialog/DeleteDialog'
import { withFrenchQueryRouter } from 'components/hocs'
import Icon from 'components/layout/Icon'
import { errorKeyToFrenchKey } from '../../utils'

class EditAndDeleteControl extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isDeleting: false,
    }
  }

  onDeleteClick = () => {
    this.setState({ isDeleting: true })
  }

  onCancelDeleteClick = () => {
    this.setState({ isDeleting: false })
  }

  handleRequestFail = formResolver => (state, action) => {
    const { handleSetErrors } = this.props
    const {
      payload: { errors },
    } = action
    const nextState = { isRequestPending: false }
    const frenchErrors = Object.keys(errors)
      .filter(errorKeyToFrenchKey)
      .reduce(
        (result, errorKey) =>
          Object.assign(
            { [errorKeyToFrenchKey(errorKey)]: errors[errorKey] },
            result
          ),
        null
      )
    this.setState(nextState, () => handleSetErrors(frenchErrors))
  }

  onConfirmDeleteClick = () => {
    const { dispatch, formInitialValues, handleSetErrors } = this.props

    handleSetErrors()

    const formSubmitPromise = new Promise(resolve => {
      dispatch(
        requestData({
          apiPath: `stocks/${formInitialValues.id}`,
          handleFail: this.handleRequestFail(resolve),
          method: 'DELETE',
        })
      )
    })
    return formSubmitPromise
  }

  render() {
    const { isEvent, query, stock } = this.props
    const { id: stockId } = stock
    const { isDeleting } = this.state

    if (!stockId) {
      return null
    }

    // Delete dialog
    if (isDeleting) {
      return (
        <td colSpan="2">
          <Portal node={this.props.tbody}>
            <DeleteDialog
              isEvent={isEvent}
              onCancelDeleteClick={this.onCancelDeleteClick}
              onConfirmDeleteClick={this.onConfirmDeleteClick}
            />
          </Portal>
        </td>
      )
    }

    return (
      <Fragment>
        <td>
          <button
            className="button is-small is-secondary edit-stock"
            id={`edit-stock-${stockId}-button`}
            onClick={() =>
              query.changeToModification(null, { id: stockId, key: 'stock' })
            }>
            <span className="icon">
              <Icon svg="ico-pen-r" />
            </span>
          </button>
        </td>
        <td className="is-clipped">
          {!isDeleting && (
            <button
              className="button is-small is-secondary delete-stock"
              style={{ width: '100%' }}
              onClick={this.onDeleteClick}>
              <span className="icon">
                <Icon svg="ico-close-r" />
              </span>
            </button>
          )}
        </td>
      </Fragment>
    )
  }
}

EditAndDeleteControl.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isEvent: PropTypes.bool.isRequired,
  query: PropTypes.object.isRequired,
  stock: PropTypes.object.isRequired,
  formInitialValues: PropTypes.object.isRequired,
  handleSetErrors: PropTypes.func.isRequired,
}

export default withFrenchQueryRouter(EditAndDeleteControl)
