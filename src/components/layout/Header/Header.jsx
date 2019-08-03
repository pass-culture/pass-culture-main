import React, { Component } from 'react'
import PropTypes from 'prop-types'

import BackLink from './BackLink'
import CloseLink from './CloseLink'
import SubmitButton from './SubmitButton'
import getIsTransitionDetailsUrl from '../../../helpers/getIsTransitionDetailsUrl'


class Header extends Component {
  componentDidMount () {
    const { history, match } = this.props

    const isTransitionDetailsUrl = getIsTransitionDetailsUrl(match)
    if (isTransitionDetailsUrl) {
      history.push(this.getRemovedTransitionUrl())
    }
  }

  componentDidUpdate (prevProps) {
    const { history, match } = this.props

    const hasTransitionJustHappened = getIsTransitionDetailsUrl(match) &&
      !getIsTransitionDetailsUrl(prevProps.match)
    if (hasTransitionJustHappened) {
      setTimeout(() => history.replace(this.getRemovedTransitionUrl()), 300)
    }
  }

  getBackTo = () => {
    const { match, shouldBackFromDetails } = this.props
    const { params } = match
    const { details } = params
    let { backTo } = this.props
    if (!backTo && shouldBackFromDetails && details === "details") {
      backTo = this.getTransitionUrl()
    }
    return backTo
  }

  getRemovedTransitionUrl = () => {
    const { location } = this.props
    const { pathname, search } = location
    return `${pathname.split('/transition')[0]}${search}`
  }

  getTransitionUrl = () => {
    const { location } = this.props
    const { pathname, search } = location
    return `${pathname.replace('/details', '/transition')}${search}`
  }

  render () {
    const {
      backActionOnClick,
      backTitle,
      closeActionOnClick,
      closeTitle,
      closeTo,
      submitDisabled,
      title,
      useSubmit,
    } = this.props
    const backTo = this.getBackTo()
    return (
      <header className="header">
        {backTo && (
          <div className="header-start">
            <BackLink
              actionOnClick={backActionOnClick}
              backTitle={backTitle}
              backTo={backTo}
            />
          </div>
        )}
        <h1 className="header-title">{title}</h1>
        {closeTo && (
          <div className="header-end">
            <CloseLink
              actionOnClick={closeActionOnClick}
              closeTitle={closeTitle}
              closeTo={closeTo}
            />
          </div>
        )}
        {useSubmit && (
          <div className="header-end">
            <SubmitButton disabled={!submitDisabled} />
          </div>
        )}
      </header>
    )
  }
}

Header.defaultProps = {
  backActionOnClick: null,
  backTitle: 'Retour',
  backTo: null,
  closeActionOnClick: null,
  closeTitle: 'Retourner à la page découverte',
  closeTo: '/decouverte',
  shouldBackFromDetails: false,
  submitDisabled: true,
  useSubmit: false,
}

Header.propTypes = {
  backActionOnClick: PropTypes.func,
  backTitle: PropTypes.string,
  backTo: PropTypes.string,
  closeActionOnClick: PropTypes.func,
  closeTitle: PropTypes.string,
  closeTo: PropTypes.string,
  history: PropTypes.shape({
    replace: PropTypes.func.isRequired,
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string
    }).isRequired
  }).isRequired,
  shouldBackFromDetails: PropTypes.bool,
  submitDisabled: PropTypes.bool,
  title: PropTypes.string.isRequired,
  useSubmit: PropTypes.bool,
}

export default Header
