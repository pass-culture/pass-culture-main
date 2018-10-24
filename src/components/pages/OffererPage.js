import classnames from 'classnames'
import get from 'lodash.get'
import {
  CancelButton,
  Field,
  Form,
  requestData,
  showNotification,
  SubmitButton,
  withLogin,
} from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import HeroSection from '../layout/HeroSection'
import VenueItem from '../items/VenueItem'
import Main from '../layout/Main'
import offererSelector from '../../selectors/offerer'
import selectPhysicalVenuesByOffererId from '../../selectors/selectPhysicalVenuesByOffererId'
import { offererNormalizer } from '../../utils/normalizers'

class OffererPage extends Component {
  constructor() {
    super()
    this.state = {
      isNew: false,
      isReadOnly: true,
    }
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      location: { search },
      match: {
        params: { offererId },
      },
    } = nextProps
    const isEdit = search.includes('modifie')
    const isNew = offererId === 'nouveau'
    const isReadOnly = !isNew && !isEdit
    return {
      isNew,
      isReadOnly,
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      dispatch,
      match: {
        params: { offererId },
      },
    } = this.props

    if (offererId !== 'nouveau') {
      dispatch(
        requestData('GET', `offerers/${offererId}`, {
          handleSuccess,
          handleFail,
          normalizer: offererNormalizer,
        })
      )
      return
    }

    handleSuccess()
  }

  handleSuccess = () => {
    const { dispatch, history } = this.props
    const { isNew } = this.props

    history.push('/structures')

    const text = isNew
      ? 'Votre structure a bien été enregistrée, elle est en cours de validation.'
      : 'Les modifications sur votre structure ont bien été pris en compte'

    dispatch(
      showNotification({
        text,
        type: 'success',
      })
    )
  }

  onAddProviderClick = () => {
    this.setState({ isNewProvider: true })
  }

  render() {
    const { offerer, sirenName, venues } = this.props
    const { isNew, isReadOnly } = this.state
    const { id } = offerer || {}
    const areSirenFieldsVisible = get(offerer, 'id') || sirenName

    const $newControl = (
      <div
        className="field is-grouped is-grouped-centered"
        style={{ justifyContent: 'space-between' }}>
        <div className="control">
          <NavLink className="button is-secondary is-medium" to="/structures">
            Retour
          </NavLink>
        </div>
        <div className="control">
          <SubmitButton className="button is-primary is-medium">
            Valider
          </SubmitButton>
        </div>
      </div>
    )

    const $editControl = (
      <Fragment>
        <div className="control">
          {isReadOnly ? (
            <NavLink
              className="button is-secondary is-medium"
              to={`/structures/${id}?modifie`}>
              Modifier la structure
            </NavLink>
          ) : (
            <div
              className="field is-grouped is-grouped-centered"
              style={{ justifyContent: 'space-between' }}>
              <div className="control">
                <CancelButton
                  className="button is-secondary is-medium"
                  to={`/structures/${id}`}>
                  Annuler
                </CancelButton>
              </div>
              <div className="control">
                <SubmitButton className="button is-primary is-medium">
                  Valider
                </SubmitButton>
              </div>
            </div>
          )}
        </div>
        <br />
        <div className="section">
          <h2 className="main-list-title">LIEUX</h2>
          <ul className="main-list venues-list">
            {venues.map(v => (
              <VenueItem key={v.id} venue={v} />
            ))}
          </ul>
          <div className="has-text-centered">
            <NavLink
              to={`/structures/${get(offerer, 'id')}/lieux/nouveau`}
              className="button is-secondary is-outlined">
              + Ajouter un lieu
            </NavLink>
          </div>
        </div>
      </Fragment>
    )

    return (
      <Main
        backTo={{ label: 'Vos structures', path: '/structures' }}
        name="offerer"
        handleDataRequest={this.handleDataRequest}>
        <HeroSection subtitle={get(offerer, 'name')} title="Structure">
          <p className="subtitle">
            Détails de la structure rattachée, des lieux et des fournisseurs de
            ses offres.
          </p>
        </HeroSection>

        <Form
          name="offerer"
          className="section"
          action={`/offerers/${get(offerer, 'id') || ''}`}
          handleSuccess={this.handleSuccess}
          patch={offerer}
          readOnly={isReadOnly}>
          <div className="field-group">
            <Field
              disabling={() => !sirenName}
              label="SIREN"
              name="siren"
              readOnly={get(offerer, 'id')}
              required
              type="siren"
            />
            <Field
              className={classnames({ 'is-invisible': !areSirenFieldsVisible })}
              isExpanded
              label="Désignation"
              name="name"
              readOnly
              required
            />
            <Field
              className={classnames({ 'is-invisible': !areSirenFieldsVisible })}
              isExpanded
              label="Siège social"
              name="address"
              readOnly
              required
            />
            <Field
              className={classnames({
                'is-invisible': !areSirenFieldsVisible,
              })}
              isExpanded
              label="BIC"
              name="bic"
              type="bic"
              required
            />
            <Field
              className={classnames({
                'is-invisible': !areSirenFieldsVisible,
              })}
              isExpanded
              label="IBAN"
              name="iban"
              type="iban"
              required
            />
          </div>

          {isNew ? $newControl : $editControl}
        </Form>
      </Main>
    )
  }
}

function mapStateToProps(state, ownProps) {
  const offererId = ownProps.match.params.offererId
  return {
    offerer: offererSelector(state, offererId),
    venues: selectPhysicalVenuesByOffererId(state, offererId),
    user: state.user,
    sirenName: get(state, 'form.offerer.name'),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  connect(mapStateToProps)
)(OffererPage)
