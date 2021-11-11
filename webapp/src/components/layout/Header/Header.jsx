import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import getIsTransitionDetailsUrl from '../../../utils/getIsTransitionDetailsUrl'
import BackLink from './BackLink/BackLink'

class Header extends PureComponent {
  componentDidMount() {
    const { history, match } = this.props

    if (getIsTransitionDetailsUrl(match)) {
      history.push(this.getRemovedTransitionUrl())
    }
  }

  componentDidUpdate(prevProps) {
    const { history, match } = this.props

    const hasTransitionJustHappened =
      getIsTransitionDetailsUrl(match) && !getIsTransitionDetailsUrl(prevProps.match)

    if (hasTransitionJustHappened) {
      history.replace(this.getRemovedTransitionUrl())
    }
  }

  getBackTo = () => {
    const { match, shouldBackFromDetails } = this.props
    const { params } = match || {}
    const { details } = params || {}
    let { backTo } = this.props
    if (!backTo && shouldBackFromDetails && details === 'details') {
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

  render() {
    const { backActionOnClick, backTitle, extraClassName, reset, title } = this.props
    const backTo = this.getBackTo()
    return (
      <header className={`header ${extraClassName}`}>
        {backTo && (
          <div className="header-start">
            <BackLink
              actionOnClick={backActionOnClick}
              backTitle={backTitle}
              backTo={backTo}
            />
          </div>
        )}
        <h1 className="header-title">
          {title}
        </h1>
        {reset && (
          <button
            className="reset-button"
            onClick={reset}
            type="button"
          >
            {'Réinitialiser'}
          </button>
        )}
      </header>
    )
  }
}

Header.defaultProps = {
  backActionOnClick: null,
  backTitle: 'Retour',
  backTo: null,
  extraClassName: '',
  reset: null,
  shouldBackFromDetails: false,
}

Header.propTypes = {
  backActionOnClick: PropTypes.func,
  backTitle: PropTypes.string,
  backTo: PropTypes.string,
  extraClassName: PropTypes.string,
  history: PropTypes.shape({
    replace: PropTypes.func.isRequired,
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  reset: PropTypes.func,
  shouldBackFromDetails: PropTypes.bool,
  title: PropTypes.string.isRequired,
}

export default Header
