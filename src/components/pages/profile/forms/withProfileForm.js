/* eslint
    react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { Form as FinalForm } from 'react-final-form'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { requestData } from 'redux-saga-data'
import { selectCurrentUser } from 'with-login'

import { ROOT_PATH } from '../../../../utils/config'
import { parseSubmitErrors } from '../../../forms/utils'
import PageHeader from '../../../layout/PageHeader'
import NavigationFooter from '../../../layout/NavigationFooter'

const noop = () => {}
const BACKGROUND_IMAGE = `url('${ROOT_PATH}/mosaic-k.png')`

const getInitialValuesFromUser = (obj, user) =>
  Object.keys(obj).reduce((acc, key) => {
    const propobj = (user[key] && { [key]: user[key] }) || { [key]: null }
    return { ...acc, ...propobj }
  }, {})

/**
 * Permet la gestion des formulaires sur la page profil
 * @param  {Component}  WrappedComponent         React Node Children
 * @param  {Function}  [validator='noop']        Function de validation du form
 *                                               par défaut ne valide pas
 * @param  {String}  [routePath='users/current'] Route de l'API pour l'update
 * @param  {String}  [routeMethod='PATCH']       Methode de la route API
 * @param  {String}  [stateKey='users']         Si au resultat de l'appel API
 *                                               Le store redux doit être update
 *                                               La valeur `false` désactive
 *                                               l'update du store/reducer
 * @param  {Boolean} [initialValues=false]       Default values du formulaire
 */
const withProfileForm = (
  WrappedComponent,
  validator = noop,
  // TODO: replace avec un object type options
  // si possible faire un typage pour vérifier que les clés existent
  // FIXME -> l'object options, peut être passé depuis la config
  // en tant que props du composant, comme pour la propriete `title` du header
  routePath = 'users/current',
  routeMethod = 'PATCH',
  stateKey = 'users',
  initialValues = false
) => {
  const name = WrappedComponent.displayName || 'Component'
  withProfileForm.displayName = `withProfileForm(${name})`

  // azertyazertyP1$
  class ProfilePasswordForm extends React.PureComponent {
    constructor(props) {
      super(props)
      const { currentUser, dispatch } = this.props
      this.state = { isloading: false }
      // NOTE: initialValues sont detruites a chaque mount/unmount
      // mais la reference ne change pas au changement du state
      this.initialValues = getInitialValuesFromUser(initialValues, currentUser)
      this.actions = bindActionCreators({ requestData }, dispatch)
    }

    handleRequestFail = formResolver => (state, action) => {
      // on retourne les erreurs API au formulaire
      const nextstate = { isloading: false }
      const {
        payload: { errors },
      } = action
      const errorsByKey = parseSubmitErrors(errors)
      this.setState(nextstate, () => formResolver(errorsByKey))
    }

    handleRequestSuccess = formResolver => () => {
      const { history, location } = this.props
      const nextstate = { isloading: false }
      this.setState(nextstate, () => {
        formResolver()
        // NOTE: si aucune erreur alors
        // on resout la promise du formulaire et on revient sur la page precedente
        const nexturl = `${location.pathname}/success`
        history.replace(nexturl)
      })
    }

    onFormSubmit = formValues => {
      this.setState({ isloading: true })
      // NOTE: on retourne une promise au formulaire
      // pour pouvoir gérer les erreurs de l'API
      // directement dans les champs du formulaire
      const formSubmitPromise = new Promise(resolve => {
        const config = {
          apiPath: routePath,
          body: { ...formValues },
          handleFail: this.handleRequestFail(resolve),
          handleSuccess: this.handleRequestSuccess(resolve),
          isMergingDatum: true,
          method: routeMethod,
        }
        // NOTE: par défaut on utilise la clé 'users'
        if (stateKey) config.key = stateKey
        this.actions.requestData(config)
      })
      return formSubmitPromise
    }

    onFormReset = () => {
      const { history } = this.props
      history.goBack()
    }

    render() {
      const { title } = this.props
      const { isloading } = this.state
      return (
        <div
          id="profile-page-form-view"
          className="pc-page-view pc-theme-default flex-rows"
        >
          <FinalForm
            validate={validator}
            onSubmit={this.onFormSubmit}
            initialValues={this.initialValues || {}}
            render={({
              // https://github.com/final-form/final-form#formstate
              dirtySinceLastSubmit,
              error: preSubmitError,
              handleSubmit,
              hasSubmitErrors,
              hasValidationErrors,
              pristine,
            }) => {
              const canSubmit =
                (!pristine &&
                  !hasSubmitErrors &&
                  !hasValidationErrors &&
                  !isloading) ||
                (!hasValidationErrors &&
                  hasSubmitErrors &&
                  dirtySinceLastSubmit)
              return (
                <form
                  noValidate
                  autoComplete="off"
                  disabled={isloading}
                  onSubmit={handleSubmit}
                  onReset={this.onFormReset}
                  className="pc-final-form flex-rows"
                >
                  <PageHeader
                    useBack
                    useSubmit
                    theme="red"
                    canSubmit={canSubmit}
                    isloading={isloading}
                    title={title}
                  />
                  <main
                    role="main"
                    style={{ backgroundImage: BACKGROUND_IMAGE }}
                    className="pc-main is-clipped is-relative flex-1"
                  >
                    <WrappedComponent
                      {...this.props}
                      isLoading={isloading}
                      formErrors={!pristine && preSubmitError}
                    />
                  </main>
                </form>
              )
            }}
          />
          <NavigationFooter
            theme="white"
            disabled={isloading}
            className="dotted-top-red"
          />
        </div>
      )
    }
  }

  ProfilePasswordForm.defaultProps = {
    title: null,
  }

  ProfilePasswordForm.propTypes = {
    currentUser: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired,
    // NOTE: history et location sont automatiquement
    // injectées par le render de la route du react-router-dom
    history: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired,
    title: PropTypes.string,
  }

  function mapStateToProps(state) {
    return {
      currentUser: selectCurrentUser(state),
    }
  }

  return connect(mapStateToProps)(ProfilePasswordForm)
}

export default withProfileForm
