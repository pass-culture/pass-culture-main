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

import HeroSection from '../../layout/HeroSection'
import VenueItem from './VenueItem'
import Main from '../../layout/Main'
import offererSelector from '../../../selectors/offerer'
import selectUserOffererByOffererIdAndUserIdAndRightsType from '../../../selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectPhysicalVenuesByOffererId from '../../../selectors/selectPhysicalVenuesByOffererId'
import { offererNormalizer } from '../../../utils/normalizers'

const OFFERER_NEW_PATCH_KEYS = [
  'address',
  'city',
  'name',
  'siren',
  'postalCode',
]
const OFFERER_EDIT_PATCH_KEYS = ['bic', 'iban', 'rib']

const formatOffererPatch = (patch, config) => {
  const { isNew } = config || {}
  const formPatch = {}

  let patchKeys = OFFERER_EDIT_PATCH_KEYS
  if (isNew) {
    patchKeys = OFFERER_NEW_PATCH_KEYS
  }

  patchKeys.forEach(key => {
    if (patch[key]) {
      formPatch[key] = patch[key]
    }
  })
  return formPatch
}

export class OffererPage extends Component {
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
      isEdit,
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

      dispatch(requestData('GET', `userOfferers/${offererId}`))

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
    const { adminUserOfferer, offerer, sirenName, venues } = this.props
    const { isEdit, isNew, isReadOnly } = this.state
    const { id } = offerer || {}
    const areSirenFieldsVisible = get(offerer, 'id') || sirenName
    const areBankInfosReadOnly = isReadOnly || !adminUserOfferer

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
          action={`/offerers/${get(offerer, 'id') || ''}`}
          name="offerer"
          className="section"
          formatPatch={patch => formatOffererPatch(patch, { isNew, isEdit })}
          handleSuccess={this.handleSuccess}
          patch={offerer}
          readOnly={isReadOnly}>
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
                {isReadOnly &&
                  !adminUserOfferer &&
                  "Vous avez besoin d'être administrateur de la structure pour editer ces informations."}
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
            {isNew ? $newControl : $editControl}
          </div>
        </Form>
      </Main>
    )
  }
}

function mapStateToProps(state, ownProps) {
  const offererId = ownProps.match.params.offererId
  const { id: userId } = state.user || {}
  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      userId,
      'admin'
    ),
    offerer: offererSelector(state, offererId),
    sirenName: get(state, 'form.offerer.name'),
    user: state.user,
    venues: selectPhysicalVenuesByOffererId(state, offererId),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  connect(mapStateToProps)
)(OffererPage)
