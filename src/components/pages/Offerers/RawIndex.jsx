import { Icon, InfiniteScroller, requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'

import OffererItem from './OffererItem'
import PendingOffererItem from './PendingOffererItem'
import HeroSection from '../../layout/HeroSection'
import Main from '../../layout/Main'
import { offererNormalizer } from '../../../utils/normalizers'
import { mapApiToWindow } from '../../../utils/pagination'

class RawOfferers extends Component {
  handleDataRequest = (handleSuccess, handleFail) => {
    const { user, dispatch, pagination, search } = this.props
    const { apiQueryString, page, goToNextPage } = pagination

    // BECAUSE THE INFINITE SCROLLER CALLS ONCE THIS FUNCTION
    // BUT THEN PUSH THE SEARCH TO PAGE + 1
    // WE PASS AGAIN HERE FOR THE SAME PAGE
    // SO WE NEED TO PREVENT A SECOND CALL
    if (page !== 1 && search.page && page === Number(search.page)) {
      return
    }

    const path = `offerers?page=${page}&${apiQueryString}`

    dispatch(
      requestData('GET', path, {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          goToNextPage()
        },
        handleFail,
        normalizer: offererNormalizer,
      })
    )

    if (!user.isAdmin) {
      dispatch(
        requestData('GET', 'offerers?validated=false', {
          handleSuccess: (state, action) => {
            handleSuccess(state, action)
          },
          handleFail,
          key: 'pendingOfferers',
        })
      )
    }
  }

  onSubmit = event => {
    const { pagination } = this.props

    event.preventDefault()

    const value = event.target.elements.search.value

    pagination.change({
      [mapApiToWindow.keywords]: value === '' ? null : value,
    })
  }

  render() {
    const { pendingOfferers, offerers, pagination } = this.props
    const { search } = pagination.apiQuery || {}

    const sectionTitle =
      offerers.length > 1
        ? 'Vos structures juridiques'
        : 'Votre structure juridique'

    return (
      <Main name="offerers" handleDataRequest={this.handleDataRequest}>
        <HeroSection title={sectionTitle}>
          <p className="subtitle">
            Pour présenter vos offres, vous devez d'abord créer un{' '}
            <b> nouveau lieu </b> lié à une structure.
            <br />
            Sans lieu, vous ne pouvez ajouter que des offres numériques.
          </p>
          <NavLink
            to={`/structures/nouveau`}
            className="cta button is-primary is-outlined">
            + Rattacher une structure supplémentaire
          </NavLink>
        </HeroSection>

        <form className="section" onSubmit={this.onSubmit}>
          <label className="label">Rechercher une structure :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                id="search"
                className="input search-input"
                placeholder="Saisissez un ou plusieurs mots complets"
                type="text"
                defaultValue={search}
              />
            </p>
            <p className="control">
              <button type="submit" className="button is-primary is-outlined">
                OK
              </button>{' '}
              <button className="button is-secondary" disabled>
                &nbsp;
                <Icon svg="ico-filter" />
                &nbsp;
              </button>
            </p>
          </div>
        </form>

        {pendingOfferers.length > 0 && (
          <ul id="pending-offerer-list" className="main-list offerers-list">
            {pendingOfferers.map(o => (
              <PendingOffererItem key={o.siren} offerer={o} />
            ))}
          </ul>
        )}

        <InfiniteScroller
          className="main-list offerers-list"
          handleLoadMore={(handleSuccess, handleFail) => {
            this.handleDataRequest(handleSuccess, handleFail)
            const { history, location, pagination } = this.props
            const { windowQueryString, page } = pagination
            history.push(
              `${location.pathname}?page=${page}&${windowQueryString}`
            )
          }}>
          {offerers.map(o => (
            <OffererItem key={o.id} offerer={o} />
          ))}
        </InfiniteScroller>
      </Main>
    )
  }
}

export default RawOfferers
