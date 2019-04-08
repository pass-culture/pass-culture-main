import classnames from 'classnames'
import get from 'lodash.get'
import { closeModal } from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'

import StockItem from './StockItem'
import HeroSection from 'components/layout/HeroSection'

const getStocksManagerButtonTitle = (isEventStock, stocks) => {
  if (isEventStock) {
    return '+ Ajouter une date'
  }
  if (stocks.length) {
    return ''
  }
  return 'Renseigner le stock'
}

class RawStocksManager extends Component {
  constructor() {
    super()
    this.state = {
      errors: null,
      info: null,
    }
  }

  componentDidMount() {
    this.handleShouldPreventCreationOfSecondNotEventStock()

    this.elem.focus()
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

  handleShouldPreventCreationOfSecondNotEventStock = () => {
    const { shouldPreventCreationOfSecondStock, query } = this.props
    const { isCreatedEntity } = query.context({ key: 'stock' })

    if (!shouldPreventCreationOfSecondStock) {
      return
    }

    if (isCreatedEntity) {
      query.changeToReadOnly(null, { key: 'stock' })
    }
  }

  handleEscKey() {
    const { query } = this.props
    const { readOnly } = query.context({ key: 'stock' })
    if (readOnly) {
      this.onCloseClick()
    } else {
      const cancelButton = document.getElementsByClassName('cancel-step')[0]
      cancelButton.click()
    }
  }

  handleEnterKey() {
    const { location, query } = this.props
    const { search } = location
    const allStocksReadOnly = !/stock([A-Z0-9]*)=(creation|modification)/.test(
      search
    )

    // Dirty DOM selectors ? Could try to pass back a react dom ref
    // to this parent component otherwise, but code would be more
    // complicated
    if (allStocksReadOnly) {
      document.getElementById('add-stock').focus()
      query.changeToCreation(null, { key: 'stock' })
    } else {
      const submitButton = document.querySelector('button[type="submit"]')
      submitButton.click()
    }
  }

  handleSetErrors = errors => {
    this.setState({ errors })
  }

  closeInfo = () => {
    this.setState({ info: null })
  }

  showInfo = info => {
    this.setState({ info })
  }

  onCloseClick = e => {
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
    const { isEventStock } = this.props
    return (
      <thead>
        <tr>
          {isEventStock && (
            <Fragment>
              <td>Date</td>
              <td>
                Heure de
                <br />
                début
              </td>
              <td>
                Heure de
                <br />
                fin
              </td>
            </Fragment>
          )}
          <td>Prix</td>
          <td>Date Limite de Réservation</td>
          <td>{isEventStock ? 'Stock affecté' : 'Places affectées'}</td>
          <td>{isEventStock ? 'Stock restant' : 'Places restantes'}</td>
          <td>Modifier</td>
          <td>Supprimer</td>
        </tr>
      </thead>
    )
  }

  render() {
    const {
      event,
      isEventStock,
      offer,
      provider,
      shouldPreventCreationOfSecondStock,
      stocks,
      thing,
      query,
    } = this.props
    const { errors, info } = this.state
    const { isCreatedEntity, readOnly } = query.context({ key: 'stock' })

    return (
      <div className="stocks-manager" ref={elem => (this.elem = elem)}>
        <div className={classnames('info', { 'is-invisible': !info })}>
          <div className="content">
            <div>{info}</div>
          </div>
        </div>

        {errors && (
          <div className="notification is-danger">
            {Object.keys(errors).map(key => (
              <p key={key}>
                {' '}
                {key} : {errors[key]}
              </p>
            ))}
          </div>
        )}
        <div className="stocks-table-wrapper">
          <HeroSection
            title={
              get(event, 'id')
                ? 'Dates, horaires et prix'
                : get(thing, 'id') && 'Prix'
            }
            subtitle={get(event, 'name') || get(thing, 'name')}
          />
          <table
            className={classnames('table is-hoverable stocks-table', {
              small: !isEventStock,
            })}>
            {this.renderTableHead()}
            {provider ? (
              <tbody>
                <tr>
                  <td colSpan="10">
                    <i>
                      Il n'est pas possible d'ajouter ni de supprimer d'horaires
                      pour cet événement {provider.name}
                    </i>
                  </td>
                </tr>
              </tbody>
            ) : (
              <tbody>
                <tr
                  className={classnames({
                    inactive: shouldPreventCreationOfSecondStock,
                  })}>
                  <td colSpan="10">
                    <button
                      className="button is-secondary"
                      disabled={!readOnly}
                      id="add-stock"
                      onClick={() =>
                        query.changeToCreation(null, { key: 'stock' })
                      }
                      type="button">
                      {getStocksManagerButtonTitle(isEventStock, stocks)}
                    </button>
                  </td>
                </tr>
              </tbody>
            )}

            {isCreatedEntity && offer && (
              <StockItem
                closeInfo={this.closeInfo}
                handleSetErrors={this.handleSetErrors}
                isFullyEditable={!provider}
                isEventStock={isEventStock}
                showInfo={this.showInfo}
              />
            )}

            {stocks.map(stock => (
              <StockItem
                closeInfo={this.closeInfo}
                key={stock.id}
                handleSetErrors={this.handleSetErrors}
                isFullyEditable={!provider}
                isEventStock={isEventStock}
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
          onClick={this.onCloseClick}>
          Fermer
        </button>
      </div>
    )
  }
}

RawStocksManager.defaultProps = {
  shouldPreventCreationOfSecondStock: false,
  stocks: [],
}

RawStocksManager.propTypes = {
  shouldPreventCreationOfSecondStock: PropTypes.bool,
  stocks: PropTypes.array,
  query: PropTypes.object.isRequired,
}

export default RawStocksManager
