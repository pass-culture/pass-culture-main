import classnames from 'classnames'
import get from 'lodash.get'
import { closeModal } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'

import Titles from 'components/layout/Titles/Titles'

import StockItemContainer from './StockItem/StockItemContainer'
import StockInformationMessage from './StockItem/utils/StockInformationMessage'

class StocksManager extends PureComponent {
  constructor() {
    super()
    this.state = {
      editSuccess: false,
      errors: null,
      info: null,
    }
  }

  componentDidMount() {
    this.handleShouldPreventCreationOfSecondNotEventStock()

    if (this.elem) {
      this.elem.focus()
    }
    document.addEventListener('keydown', this.onKeydown)
  }

  componentDidUpdate(prevProps) {
    const { stocks } = this.props
    if (stocks !== prevProps.stocks) {
      this.handleShouldPreventCreationOfSecondNotEventStock()
    }
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.onKeydown)
  }

  getStocksManagerButtonTitle = (isEvent, stocks) => {
    if (isEvent) {
      return '+ Ajouter une date'
    }
    if (stocks.length) {
      return ''
    }
    return 'Renseigner le stock'
  }

  handleEscKey() {
    const { query } = this.props
    const { readOnly } = query.context({ key: 'stock' })
    if (readOnly) {
      this.handleOnCloseClick()
    } else {
      const cancelButton = document.getElementsByClassName('cancel-step')[0]
      cancelButton.click()
    }
  }

  handleEnterKey() {
    const { location, query, isStockCreationAllowed } = this.props
    const { search } = location
    const isCreatingOrUpdating = !/stock([A-Z0-9]*)=(creation|modification)/.test(search)

    if (isCreatingOrUpdating) {
      if (!isStockCreationAllowed) {
        return
      }

      const addStockButton = document.getElementById('add-stock')
      if (addStockButton) {
        addStockButton.focus()
      }

      query.changeToCreation(null, { key: 'stock' })
    } else {
      const submitButton = document.querySelector('button[type="submit"]')
      submitButton.click()
    }
  }

  handleShouldPreventCreationOfSecondNotEventStock = () => {
    const { isStockCreationAllowed, query } = this.props
    const { isCreatedEntity } = query.context({ key: 'stock' })

    if (!isStockCreationAllowed && isCreatedEntity) {
      query.changeToReadOnly(null, { key: 'stock' })
    }
  }

  onHandleSetErrors = errors => {
    this.setState({ errors })
  }

  onHandleEditSuccess = () => {
    this.setState({ editSuccess: true }, () => {
      setTimeout(() => {
        this.setState({ editSuccess: false })
      }, 4000)
    })
  }

  closeInfo = () => {
    this.setState({ info: null })
  }

  showInfo = info => {
    this.setState({ info })
  }

  handleOnCloseClick = () => {
    const { dispatch, query } = this.props
    dispatch(closeModal())
    query.change({ gestion: null })
  }

  onKeydown = event => {
    if (event.key === 'Enter') {
      this.handleEnterKey()
    } else if (event.key === 'Escape') {
      this.handleEscKey()
    }
  }

  renderTableHead() {
    const { isEvent } = this.props
    return (
      <thead>
        <tr>
          {isEvent && (
            <Fragment>
              <td>
                {'Date'}
              </td>
              <td>
                {'Heure de'}
                <br />
                {'début'}
              </td>
            </Fragment>
          )}
          <td>
            {'Prix'}
          </td>
          <td>
            {'Date Limite de Réservation'}
          </td>
          <td>
            {'Stock total'}
          </td>
          <td>
            {'Stock restant'}
          </td>
          <td>
            {'Réservations'}
          </td>
          <td>
            {'Modifier'}
          </td>
          <td>
            {'Supprimer'}
          </td>
        </tr>
      </thead>
    )
  }

  handleOnClickCreateStockItem = () => {
    const { query } = this.props

    query.changeToCreation(null, {
      key: 'stock',
    })
  }

  render() {
    const { isEvent, offer, product, provider, query, isStockCreationAllowed, stocks } = this.props
    const { editSuccess, errors, info } = this.state
    const { isCreatedEntity, readOnly } = query.context({ key: 'stock' })

    return (
      <div className="stocks-manager">
        {info && (
          <div className="info">
            <div className="content">
              <div>
                {info}
              </div>
            </div>
          </div>
        )}

        {errors && (
          <div className="notification is-danger">
            {Object.keys(errors).map(key => (
              <p key={key}>
                {`${key} : ${errors[key]}`}
              </p>
            ))}
          </div>
        )}

        <div className={classnames('notification is-success', { 'fade-out': !editSuccess })}>
          {'Les modifications ont été enregistrées.'}
          <br />
          {
            "Si la date de l'évènement a été modifiée, les utilisateurs ayant déjà réservé cette offre seront prévenus par email."
          }
        </div>

        <div className="stocks-table-wrapper">
          <Titles
            subtitle={get(offer, 'name')}
            title={isEvent ? 'Dates, horaires et prix' : get(product, 'id') && 'Prix'}
          />
          {isEvent && (
            <div className="stocks-event-legal-warning">
              <span>
                {
                  "Les réservations peuvent être annulées par les utilisateurs jusque 72h avant le début de l'événement."
                }
              </span>
              <span>
                {
                  "Si la date limite de réservation n'est pas encore passée, la place est alors automatiquement remise en vente."
                }
              </span>
            </div>
          )}
          <table className="stocks-table">
            {this.renderTableHead()}
            {provider ? (
              <tbody>
                <tr>
                  <td colSpan="10">
                    <StockInformationMessage providerName={provider.name} />
                  </td>
                </tr>
              </tbody>
            ) : (
              <tbody
                className={classnames({
                  inactive: !isStockCreationAllowed,
                })}
              >
                <tr>
                  <td colSpan="10">
                    <button
                      className="button is-tertiary"
                      disabled={!readOnly}
                      id="add-stock"
                      onClick={this.handleOnClickCreateStockItem}
                      type="button"
                    >
                      {this.getStocksManagerButtonTitle(isEvent, stocks)}
                    </button>
                  </td>
                </tr>
              </tbody>
            )}

            {isCreatedEntity && offer && (
              <StockItemContainer
                closeInfo={this.closeInfo}
                handleSetErrors={this.onHandleSetErrors}
                isEvent={isEvent}
                isFullyEditable={!provider}
                showInfo={this.showInfo}
              />
            )}

            {stocks.map(stock => (
              <StockItemContainer
                closeInfo={this.closeInfo}
                handleEditSuccess={this.onHandleEditSuccess}
                handleSetErrors={this.onHandleSetErrors}
                isEvent={isEvent}
                isFullyEditable={!provider}
                key={stock.id}
                showInfo={this.showInfo}
                stock={stock}
                stocks={stocks}
              />
            ))}

            {Math.max(get(stocks, 'length', 0)) > 12 && this.renderTableHead()}
          </table>
        </div>
        <button
          className="button is-tertiary is-pulled-right"
          id="close-manager"
          onClick={this.handleOnCloseClick}
          type="button"
        >
          {'Fermer'}
        </button>
      </div>
    )
  }
}

StocksManager.defaultProps = {
  provider: null,
  stocks: [],
}

StocksManager.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isEvent: PropTypes.bool.isRequired,
  isStockCreationAllowed: PropTypes.bool.isRequired,
  offer: PropTypes.shape().isRequired,
  product: PropTypes.shape().isRequired,
  provider: PropTypes.shape(),
  query: PropTypes.shape().isRequired,
  stocks: PropTypes.arrayOf(PropTypes.shape()),
}

export default StocksManager
