import classnames from 'classnames'
import get from 'lodash.get'
import {
  CancelButton,
  Field,
  Form,
  showNotification,
  SubmitButton,
} from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import VenueItem from './VenueItem'
import {
  OFFERER_CREATION_PATCH_KEYS,
  OFFERER_MODIFICATION_PATCH_KEYS,
} from './utils'
import HeroSection from 'components/layout/HeroSection'
import Main from 'components/layout/Main'
import { offererNormalizer } from 'utils/normalizers'
import { formatPatch } from 'utils/formatPatch'

class Offerer extends Component {
  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      dispatch,
      match: {
        params: { offererId },
      },
      query,
    } = this.props
    const { isCreatedEntity } = query.context()

    if (!isCreatedEntity) {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          handleSuccess,
          handleFail,
          normalizer: offererNormalizer,
        })
      )

      dispatch(requestData({ apiPath: `/userOfferers/${offererId}` }))

      return
    }

    handleSuccess()
  }

  handleSuccess = () => {
    const { dispatch, history } = this.props
    const { isCreatedEntity } = this.props

    history.push('/structures')

    const text = isCreatedEntity
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
    this.setState({ isCreatedEntityProvider: true })
  }

  render() {
    const { adminUserOfferer, offerer, query, sirenName, venues } = this.props
    const { isCreatedEntity, isModifiedEntity, readOnly } = query.context()
    const { id } = offerer || {}
    const areSirenFieldsVisible = get(offerer, 'id') || sirenName
    const areBankInfosReadOnly = readOnly || !adminUserOfferer

    const patchConfig = { isCreatedEntity, isModifiedEntity }

    const $creationControl = (
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

    const $modificationControl = (
      <Fragment>
        <div className="control">
          {readOnly ? (
            adminUserOfferer && (
              <NavLink
                className="button is-secondary is-medium"
                to={`/structures/${id}?modifie`}>
                Modifier les informations
              </NavLink>
            )
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
              to={`/structures/${get(offerer, 'id')}/lieux/creation`}
              className="button is-secondary is-outlined">
              + Ajouter un lieu
            </NavLink>
          </div>
        </div>
      </Fragment>
    )

    return (
      <Main
        backTo={{ label: 'Vos structures juridiques', path: '/structures' }}
        name="offerer"
        handleDataRequest={this.handleDataRequest}>
        <HeroSection subtitle={get(offerer, 'name')} title="Structure">
          <p className="subtitle">
            Détails de la structure rattachée, des lieux et des fournisseurs de
            ses offres.
          </p>
        </HeroSection>

        <Form
          action={`/offerers/${get(offerer, 'id') || ''}`}
          name="offerer"
          className="section"
          formatPatch={patch =>
            formatPatch(
              patch,
              patchConfig,
              OFFERER_CREATION_PATCH_KEYS,
              OFFERER_MODIFICATION_PATCH_KEYS
            )
          }
          handleSuccess={this.handleSuccess}
          patch={offerer}
          readOnly={readOnly}>
          <div className="section">
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
                className={classnames({
                  'is-invisible': !areSirenFieldsVisible,
                })}
                isExpanded
                label="Désignation"
                name="name"
                readOnly
                required
              />
              <Field
                className={classnames({
                  'is-invisible': !areSirenFieldsVisible,
                })}
                isExpanded
                label="Siège social"
                name="address"
                readOnly
              />
            </div>
          </div>
          <div className="section">
            <h2 className="main-list-title">
              INFORMATIONS BANCAIRES
              <span className="is-pulled-right is-size-7 has-text-grey">
                {readOnly &&
                  !adminUserOfferer &&
                  "Vous avez besoin d'être administrateur de la structure pour modifier ces informations."}
              </span>
            </h2>
            <div className="field-group">
              <Field
                className={classnames({
                  'is-invisible': !areSirenFieldsVisible,
                })}
                isExpanded
                label="BIC"
                name="bic"
                type="bic"
                readOnly={areBankInfosReadOnly}
              />
              <Field
                className={classnames({
                  'is-invisible': !areSirenFieldsVisible,
                })}
                isExpanded
                label="IBAN"
                name="iban"
                type="iban"
                readOnly={areBankInfosReadOnly}
              />
            </div>
            {isCreatedEntity ? $creationControl : $modificationControl}
          </div>
        </Form>
      </Main>
    )
  }
}

export default Offerer
