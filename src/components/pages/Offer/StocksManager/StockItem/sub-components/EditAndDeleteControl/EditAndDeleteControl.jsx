import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Portal } from 'react-portal'

import withFrenchQueryRouter from 'components/hocs/withFrenchQueryRouter'
import Icon from 'components/layout/Icon'

import { errorKeyToFrenchKey } from '../../utils/utils'
import DeleteDialog from '../DeleteDialog/DeleteDialog'

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
    const { deleteStock, formInitialValues } = this.props

    const formSubmitPromise = new Promise(resolve => {
      deleteStock(formInitialValues.id, this.handleRequestFail(resolve))
    })
    return formSubmitPromise
  }

  render() {
    const { isEvent, query, stock, tbody } = this.props
    const { id: stockId, isEventExpired, isEventDeletable } = stock
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
            className="button is-small is-tertiary edit-stock"
            disabled={isEventExpired}
            id={`edit-stock-${stockId}-button`}
            onClick={this.handleOnClick(query, stockId)}
            title={isEventExpired ? 'Les évènements passés ne sont pas modifiables' : ''}
            type="button"
          >
            <span className="icon">
              <Icon
                alt="Modifier"
                svg="ico-pen"
              />
            </span>
          </button>
        </td>
        <td className="is-clipped">
          {!isDeleting && (
            <button
              className="button is-small is-tertiary delete-stock"
              disabled={!isEventDeletable}
              onClick={this.handleOnDeleteClick}
              style={{ width: '100%' }}
              title={
                isEventDeletable
                  ? ''
                  : 'Les évènements terminés depuis plus de 48 heures ne peuvent être supprimés'
              }
              type="button"
            >
              <span className="icon">
                <Icon
                  alt="Supprimer"
                  svg="ico-close-r"
                />
              </span>
            </button>
          )}
        </td>
      </Fragment>
    )
  }
}

EditAndDeleteControl.propTypes = {
  deleteStock: PropTypes.func.isRequired,
  formInitialValues: PropTypes.shape().isRequired,
  handleSetErrors: PropTypes.func.isRequired,
  isEvent: PropTypes.bool.isRequired,
  query: PropTypes.shape().isRequired,
  stock: PropTypes.shape().isRequired,
}

export default withFrenchQueryRouter(EditAndDeleteControl)
