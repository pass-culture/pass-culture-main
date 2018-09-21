/* eslint
  react/jsx-one-expression-per-line: 0 */
import { requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'
import { Form as FinalForm } from 'react-final-form'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { bindActionCreators, compose } from 'redux'

import { ROOT_PATH } from '../../../../utils/config'
import { FormError } from '../../../forms'
import { isEmpty } from '../../../../utils/strings'
import { PasswordField } from '../../../forms/inputs'
import PageHeader from '../../../layout/PageHeader'
import NavigationFooter from '../../../layout/NavigationFooter'
import validatePasswordForm from '../validators/validatePasswordForm'

// NOTE: les anciens mot de passe lors de la phase beta
// n'avaient de règle de validation
// FIXME: peu être mettre un if avec une version du package.json
// si on considére que la v1 correspond à la mise en ligne d'octobre
const ERROR_OLD_PASSWORD = "L'ancien mot de passe est manquant"

const parseSubmitErrors = errors =>
  Object.keys(errors).reduce((acc, key) => {
    // FIXME -> test avec un array d'erreurs
    // a deplacer dans un tests unitaires
    // const err = errors[key].concat('toto')
    const err = errors[key]
    return { ...acc, [key]: err }
  }, {})

const initialValues = {
  newPassword: null,
  newPasswordConfirm: null,
  oldPassword: null,
}

// azertyazertyP1$
class ProfilePasswordForm extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = this.props
    this.state = { isloading: false }
    // NOTE: initialValues sont detruites a chaque mount/unmount
    // mais la reference ne change pas au changement du state
    this.initialValues = Object.assign({}, initialValues)
    this.actions = bindActionCreators({ requestData }, dispatch)
  }

  handleRequestFail = formResolver => (state, action) => {
    // on retourne les erreurs API au formulaire
    const nextstate = { isloading: false }
    const errors = parseSubmitErrors(action.errors)
    this.setState(nextstate, () => formResolver(errors))
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
      const route = 'users/current/change-password'
      this.actions.requestData('POST', route, {
        body: { ...formValues },
        handleFail: this.handleRequestFail(resolve),
        handleSuccess: this.handleRequestSuccess(resolve),
        // NOTE; on met pas le store du user a jour car le store
        // ne contient pas le mot de passe
        // key: 'user',
      })
    })
    return formSubmitPromise
  }

  onFormReset = () => {
    const { history } = this.props
    history.goBack()
  }

  render() {
    const { isloading } = this.state
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
    return (
      <div
        id="profile-page-password-view"
        className="pc-page-view pc-theme-default flex-rows"
      >
        <FinalForm
          onSubmit={this.onFormSubmit}
          validate={validatePasswordForm}
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
              (!hasSubmitErrors && !hasValidationErrors && !isloading) ||
              (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)
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
                  title="Mot de passe"
                />
                <main
                  role="main"
                  className="pc-main is-clipped is-relative flex-1"
                  style={{ backgroundImage }}
                >
                  <div className="pc-scroll-container">
                    <div className="padded flex-1">
                      <PasswordField
                        required={value => {
                          if (value && !isEmpty(value)) return undefined
                          return ERROR_OLD_PASSWORD
                        }}
                        name="oldPassword"
                        disabled={isloading}
                        label="Saisissez votre mot de passe actuel"
                      />
                      <PasswordField
                        required
                        className="mt36"
                        name="newPassword"
                        disabled={isloading}
                        label="Saisissez votre nouveau mot de passe"
                      />
                      <PasswordField
                        required
                        className="mt36"
                        name="newPasswordConfirm"
                        disabled={isloading}
                        label="Confirmez votre nouveau mot de passe"
                      />
                      {!pristine &&
                        preSubmitError && (
                          <FormError customMessage={preSubmitError} />
                        )}
                    </div>
                  </div>
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

ProfilePasswordForm.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
}

export default compose(
  withRouter,
  connect()
)(ProfilePasswordForm)
