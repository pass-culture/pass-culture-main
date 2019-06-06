import PropTypes from 'prop-types'
import classnames from 'classnames'
import get from 'lodash.get'
import { Modal, resetForm, showNotification } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose, bindActionCreators } from 'redux'

import BackButton from './BackButton'
import { selectCurrentUser } from '../hocs'

export class RawMain extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = props
    const actions = { resetForm, showNotification }
    this.actions = bindActionCreators(actions, dispatch)
  }

  componentDidMount() {
    const { currentUser } = this.props
    // si un utilisateur est connecte ?
    // FIXME -> cela doit etre gere par un composant private
    // heritage de ReactRouter
    // NOTE -> https://reacttraining.com/react-router/web/example/auth-workflow
    if (!currentUser) return
    this.dataRequestHandler()
  }

  componentDidUpdate(prevProps) {
    const { currentUser, location } = this.props
    const currentUserChanged = !prevProps.currentUser && currentUser // User just loaded
    const searchChanged = location.search !== prevProps.location.search

    if (currentUserChanged || searchChanged) {
      this.dataRequestHandler()
    }
  }

  componentWillUnmount() {
    this.actions.resetForm()
  }

  handleDataFail = (state, action) => {
    const { payload } = action
    const error = get(payload, 'errors.global', []).join('\n')
    this.actions.showNotification({
      text: error || 'Erreur de chargement',
      type: 'danger',
    })
  }

  dataRequestHandler = () => {
    const { handleDataRequest } = this.props
    // la definition d'une propriete `handleDataRequest`
    // dans un composant lance une requete

    if (!handleDataRequest) return
    // possibility of the handleDataRequest to return
    // false in order to not trigger the loading
    handleDataRequest(this.handleDataSuccess, this.handleDataFail)
  }

  closeHandler = () => {
    const { history } = this.props
    history.push('/decouverte')
  }

  renderCloseButton = () => (
    <button
      type="button"
      id="search-close-button"
      className="pc-text-button is-absolute fs16"
      onClick={this.closeHandler}
    >
      <span
        aria-hidden
        className="icon-legacy-close is-white-text"
        title="Fermer la popin de partage"
      />
    </button>
  )

  render() {
    const {
      backButton,
      children,
      closeSearchButton,
      name,
      noPadding,
      redBg,
      footer,
      header,
      pageTitle,
    } = this.props
    // FIXME [PERFS] -> ne pas faire une itération
    // utiliser plutot une propriete avec un composant
    // const footer = [].concat(children).find(e => e.type === 'footer')
    // const content = [].concat(children).filter(e => e.type !== 'footer')

    return (
      <React.Fragment>
        <main
          role="main"
          className={classnames({
            [`${name}-page`]: true,
            'no-padding': noPadding,
            page: true,
            'red-bg': redBg,
            'with-footer': footer !== null,
            // Boolean(footer) || Boolean(footerProps),
            'with-header': header !== null,
          })}
        >
          {header && header(pageTitle)}
          {closeSearchButton && this.renderCloseButton()}
          {backButton && <BackButton {...backButton} />}
          <div className="page-content is-relative">{children}</div>
          {footer && footer()}
          {/* || (footerProps && <Footer {...footerProps} />)} */}
        </main>
        <Modal />
      </React.Fragment>
    )
  }
}

RawMain.defaultProps = {
  backButton: false,
  closeSearchButton: false,
  currentUser: null,
  footer: null,
  handleDataRequest: null,
  header: null,
  noPadding: false,
  pageTitle: null,
  redBg: false,
}

RawMain.propTypes = {
  backButton: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
  children: PropTypes.node.isRequired,
  closeSearchButton: PropTypes.bool,
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
  dispatch: PropTypes.func.isRequired,
  footer: PropTypes.func,
  handleDataRequest: PropTypes.func,
  header: PropTypes.func,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  name: PropTypes.string.isRequired,
  noPadding: PropTypes.bool,
  pageTitle: PropTypes.string,
  redBg: PropTypes.bool,
}

const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
  notification: state.notification,
})

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawMain)
