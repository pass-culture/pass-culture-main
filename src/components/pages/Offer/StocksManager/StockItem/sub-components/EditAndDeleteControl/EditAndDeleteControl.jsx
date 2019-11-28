import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'
import { Portal } from 'react-portal'
import { requestData } from 'redux-saga-data'

import DeleteDialog from '../DeleteDialog/DeleteDialog'
import withFrenchQueryRouter from '../../../../../../hocs/withFrenchQueryRouter'
import Icon from '../../../../../../layout/Icon'
import { errorKeyToFrenchKey } from '../../utils/utils'

class EditAndDeleteControl extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isDeleting: false,
    }
  }

  handleOnDeleteClick = () => {
    this.setState({ isDeleting: true })
  }

  handleOnCancelDeleteClick = () => {
    this.setState({ isDeleting: false })
  }

  handleRequestFail = () => (state, action) => {
    const { handleSetErrors } = this.props
    const {
      payload: { errors },
    } = action
    const nextState = { isRequestPending: false }
    const frenchErrors = Object.keys(errors)
      .filter(errorKeyToFrenchKey)
      .reduce(
        (result, errorKey) =>
          Object.assign({ [errorKeyToFrenchKey(errorKey)]: errors[errorKey] }, result),
        null
      )
    this.setState(nextState, () => handleSetErrors(frenchErrors))
  }

  handleOnClick = (query, stockId) => () =>
    query.changeToModification(null, { id: stockId, key: 'stock' })

  handleOnConfirmDeleteClick = () => {
    const { dispatch, formInitialValues } = this.props

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
    const { isEvent, query, stock, tbody } = this.props
    const { id: stockId } = stock
    const { isDeleting } = this.state

    if (!stockId) {
      return null
    }

    // Delete dialog
    if (isDeleting) {
      return (
        <td colSpan="2">
          <Portal node={tbody}>
            <DeleteDialog
              isEvent={isEvent}
              onCancelDeleteClick={this.handleOnCancelDeleteClick}
              onConfirmDeleteClick={this.handleOnConfirmDeleteClick}
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
            onClick={this.handleOnClick(query, stockId)}
            type="button"
          >
            <span className="icon">
              <Icon svg="ico-pen-r" />
            </span>
          </button>
        </td>
        <td className="is-clipped">
          {!isDeleting && (
            <button
              className="button is-small is-secondary delete-stock"
              onClick={this.handleOnDeleteClick}
              style={{ width: '100%' }}
              type="button"
            >
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
  formInitialValues: PropTypes.shape().isRequired,
  handleSetErrors: PropTypes.func.isRequired,
  isEvent: PropTypes.bool.isRequired,
  query: PropTypes.shape().isRequired,
  stock: PropTypes.shape().isRequired,
}

export default withFrenchQueryRouter(EditAndDeleteControl)
