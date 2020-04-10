import get from 'lodash.get'
import classnames from 'classnames'
import { closeModal } from 'pass-culture-shared'
import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'

import StockInformationMessage from './StockItem/utils/StockInformationMessage'
import StockItemContainer from './StockItem/StockItemContainer'
import Titles from '../../../layout/Titles/Titles'

class StocksManager extends PureComponent {
  constructor() {
    super()
    this.state = {
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
    const { errors, info } = this.state
    const { isCreatedEntity, readOnly } = query.context({ key: 'stock' })

    return (
      <div className="stocks-manager">
        <div className={classnames('info', { 'is-invisible': !info })}>
          <div className="content">
            <div>
              {info}
            </div>
          </div>
        </div>

        {errors && (
          <div className="notification is-danger">
            {Object.keys(errors).map(key => (
              <p key={key}>
                {`${key} : ${errors[key]}`}
              </p>
            ))}
          </div>
        )}
        <div className="stocks-table-wrapper">
          <Titles
            subtitle={get(offer, 'name')}
            title={isEvent ? 'Dates, horaires et prix' : get(product, 'id') && 'Prix'}
          />
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
              <tbody>
                <tr
                  className={classnames({
                    inactive: !isStockCreationAllowed,
                  })}
                >
                  <td colSpan="10">
                    <button
                      className="button is-secondary"
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
          className="button is-secondary is-pulled-right"
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
  stocks: [],
}

StocksManager.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isEvent: PropTypes.bool.isRequired,
  isStockCreationAllowed: PropTypes.bool.isRequired,
  offer: PropTypes.shape().isRequired,
  product: PropTypes.shape().isRequired,
  provider: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  stocks: PropTypes.arrayOf(PropTypes.shape()),
}

export default StocksManager
