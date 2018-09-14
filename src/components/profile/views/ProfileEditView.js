/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Form as FinalForm } from 'react-final-form'

import { ROOT_PATH } from '../../../utils/config'
import { InputField } from '../../forms/inputs'
import PageHeader from '../../layout/PageHeader'
import FormFooter from '../../layout/FormFooter'

const ProfileEditView = ({ match: { params }, user }) => {
  const { view } = params
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  const initialValues = Object.assign({}, user)
  console.log('initialValues', initialValues)
  const defaultValue = initialValues[view]
  return (
    <div
      id="profile-page-edit-view"
      className="pc-page-view transition-item pc-theme-default flex-rows"
    >
      <PageHeader theme="red" title="Editer Mon profil" />
      <main
        role="main"
        className="pc-main is-relative flex-1"
        style={{ backgroundImage }}
      >
        <FinalForm
          onSubmit={() => {}}
          initialValues={initialValues || {}}
          render={({ handleSubmit, invalid, pristine }) => {
            const canSubmit = !(pristine || invalid)
            return (
              <form
                onReset={() => {
                  console.log('reset form')
                }}
                onSubmit={handleSubmit}
                className="is-full-layout flex-rows"
              >
                <div className="padded-2x flex-1">
                  <InputField
                    name={view}
                    label="Field label"
                    defaultValue={defaultValue}
                  />
                </div>
                <FormFooter
                  canCancel
                  canSubmit={canSubmit}
                  submitLabel="Modifier"
                />
              </form>
            )
          }}
        />
      </main>
    </div>
  )
}

ProfileEditView.propTypes = {
  match: PropTypes.object.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default connect(mapStateToProps)(ProfileEditView)
