import classnames from 'classnames'
import get from 'lodash.get'
import {
  closeNotification,
  Field,
  Form,
  requestData,
  showNotification,
  SubmitButton,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import VenueItem from '../VenueItem'
import Main from '../layout/Main'
import offererSelector from '../../selectors/offerer'
import venuesSelector from '../../selectors/venues'
import { offererNormalizer } from '../../utils/normalizers'

class OffererPage extends Component {
  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match: {
        params: { offererId },
      },
      requestData,
    } = this.props
    if (offererId !== 'nouveau') {
      requestData('GET', `offerers/${offererId}`, {
        handleSuccess,
        handleFail,
        normalizer: offererNormalizer,
      })
      return
    }

    // prevent loading
    handleSuccess()
  }

  handleSuccess = () => {
    const { history, showNotification } = this.props
    history.push('/structures')
    showNotification({
      text:
        'Votre structure a bien été enregistrée, elle est en cours de validation.',
      type: 'success',
    })
  }

  onAddProviderClick = () => {
    this.setState({ isNewProvider: true })
  }

  render() {
    const { offerer, venues, fetchedName } = this.props

    const hasOffererName = get(offerer, 'name') || fetchedName

    return (
      <Main
        backTo={{ label: 'Vos structures', path: '/structures' }}
        name="offerer"
        handleDataRequest={this.handleDataRequest}>
        <div className="section hero">
          <h2 className="subtitle has-text-weight-bold">
            {get(offerer, 'name')}
          </h2>
          <h1 className="main-title">Structure</h1>
          <p className="subtitle">
            Détails de la structure rattachée, des lieux et des fournisseurs de
            ses offres.
          </p>
        </div>

        <Form
          name="offerer"
          className="section"
          action={`/offerers/${get(offerer, 'id') || ''}`}
          handleSuccess={this.handleSuccess}
          patch={offerer}>
          <div className="field-group">
            <Field
              label="SIREN"
              name="siren"
              readOnly={get(offerer, 'id')}
              required
              type="siren"
            />
            <Field
              className={classnames({ 'is-invisible': hasOffererName })}
              isExpanded
              label="Désignation"
              name="name"
              readOnly
              required
            />
            <Field
              className={classnames({ 'is-invisible': hasOffererName })}
              isExpanded
              label="Siège social"
              name="address"
              readOnly
              required
            />
          </div>

          {!get(offerer, 'id') ? (
            <div>
              <hr />
              <div
                className="field is-grouped is-grouped-centered"
                style={{ justifyContent: 'space-between' }}>
                <div className="control">
                  <NavLink
                    className="button is-secondary is-medium"
                    to="/structures">
                    Retour
                  </NavLink>
                </div>
                <div className="control">
                  <SubmitButton className="button is-primary is-medium">
                    Valider
                  </SubmitButton>
                </div>
              </div>
            </div>
          ) : (
            <div className="section">
              <h2 className="main-list-title">LIEUX</h2>
              <ul className="main-list venues-list">
                {venues.map(v => <VenueItem key={v.id} venue={v} />)}
              </ul>
              <div className="has-text-centered">
                <NavLink
                  to={`/structures/${get(offerer, 'id')}/lieux/nouveau`}
                  className="button is-secondary is-outlined">
                  + Ajouter un lieu
                </NavLink>
              </div>
            </div>
          )}
        </Form>
      </Main>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const offererId = ownProps.match.params.offererId
      return {
        offerer: offererSelector(state, offererId),
        venues: venuesSelector(state, offererId),
        user: state.user,
        fetchedName: get(state, 'form.offerer.name'),
      }
    },
    {
      closeNotification,
      requestData,
      showNotification,
    }
  )
)(OffererPage)
