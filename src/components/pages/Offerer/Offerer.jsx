import classnames from 'classnames'
import get from 'lodash.get'
import { Field, Form, showNotification } from 'pass-culture-shared'
import React, { Component } from 'react'
import { requestData } from 'redux-saga-data'

import CreationControl from './controls/CreationControl'
import ModificationControl from './controls/ModificationControl'
import { OFFERER_CREATION_PATCH_KEYS, OFFERER_MODIFICATION_PATCH_KEYS } from './utils'
import HeroSection from '../../layout/HeroSection/HeroSection'
import Main from '../../layout/Main'
import { offererNormalizer } from '../../../utils/normalizers'
import { formatPatch } from '../../../utils/formatPatch'

class Offerer extends Component {
  onHandleDataRequest = (handleSuccess, handleFail) => {
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

  onHandleFail = () => {
    const { dispatch } = this.props
    dispatch(
      showNotification({
        text: 'Vous étes déjà rattaché à cette structure.',
        type: 'danger',
      })
    )
  }

  onHandleSuccess = () => {
    const { dispatch, history } = this.props
    const { isCreatedEntity } = this.props

    history.push('/structures')

    const text = isCreatedEntity
      ? 'Votre structure a bien été enregistrée, elle est en cours de validation.'
      : 'Les modifications sur votre structure ont bien été prises en compte.'

    dispatch(
      showNotification({
        text,
        type: 'success',
      })
    )
  }

  handleDisabling = offererName => () => !offererName

  formatPatch = patchConfig => patch =>
    formatPatch(patch, patchConfig, OFFERER_CREATION_PATCH_KEYS, OFFERER_MODIFICATION_PATCH_KEYS)

  render() {
    const { adminUserOfferer, offerer, query, offererName } = this.props
    const { isCreatedEntity, isModifiedEntity, readOnly } = query.context()
    const areSirenFieldsVisible = get(offerer, 'id') || offererName
    const areBankInfosReadOnly = readOnly || !adminUserOfferer

    const patchConfig = { isCreatedEntity, isModifiedEntity }

    return (
      <Main
        backTo={{ label: 'Vos structures juridiques', path: '/structures' }}
        handleDataRequest={this.onHandleDataRequest}
        name="offerer"
      >
        <HeroSection
          subtitle={get(offerer, 'name')}
          title="Structure"
        >
          <p className="subtitle">
            {'Détails de la structure rattachée, des lieux et des fournisseurs de ses offres.'}
          </p>
        </HeroSection>

        <Form
          action={`/offerers/${get(offerer, 'id') || ''}`}
          className="section"
          formatPatch={this.formatPatch(patchConfig)}
          handleFail={this.onHandleFail}
          handleSuccess={this.onHandleSuccess}
          name="offerer"
          patch={offerer}
          readOnly={readOnly}
        >
          <div className="section">
            <div className="field-group">
              <Field
                disabling={this.handleDisabling(offererName)}
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
              {'INFORMATIONS BANCAIRES'}
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
                readOnly={areBankInfosReadOnly}
                type="bic"
              />
              <Field
                className={classnames({
                  'is-invisible': !areSirenFieldsVisible,
                })}
                isExpanded
                label="IBAN"
                name="iban"
                readOnly={areBankInfosReadOnly}
                type="iban"
              />
            </div>
            {isCreatedEntity ? <CreationControl /> : <ModificationControl {...this.props} />}
          </div>
        </Form>
      </Main>
    )
  }
}

export default Offerer
