import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { requestData } from '../../reducers/data'
import { resetForm } from '../../reducers/form'
import selectCurrentOfferer from '../../selectors/currentOfferer'
import { collectionToPath } from '../../utils/translate'
import { NEW } from '../../utils/config'


class OffererPage extends Component {

  componentWillUnmount() {
    this.props.resetForm()
  }

  render () {
    const {
      address,
      bookingEmail,
      offererId,
      venue
    } = this.props
    const {
      name,
      id,
      siret
    } = (venue || {})
    const isNew = offererId === 'nouveau'
    const isLoading = !(this.props.id || isNew)
    const method = isNew ? 'POST' : 'PATCH'
    const venueId = isNew ? NEW : id
    const submitPath = isNew ? `venues/` : `venues/${venueId}`
    return (
      <PageWrapper name='offer' loading={isLoading}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to={`/${collectionToPath('venues')}`} className="button is-primary is-outlined">Retour</NavLink>
            </div>

            <h1 className='title has-text-centered'>{isNew ? 'Créer' : 'Modifier'} un lieu</h1>
            <form onSubmit={this.save}>
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={siret}
              entityId={venueId}
              label={<Label title="Siret" />}
              name="siret"
              type="siret"
            />
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={name}
              entityId={venueId}
              label={<Label title="Nom" />}
              name="name"
            />
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={address || ''}
              entityId={venueId}
              label={<Label title="Adresse" />}
              name="address"
              type="adress"
            />
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={bookingEmail || ''}
              entityId={venueId}
              label={<Label title="Email de réservation" />}
              name="bookingEmail"
            />
            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                <SubmitButton
                  getBody={form => form.venuesById[venueId]}
                  getIsDisabled={form =>
                    isNew
                      ? !get(form, `venuesById.${venueId}.name`) &&
                        !get(form, `venuesById.${venueId}.adress`)
                      : !get(form, `venuesById.${venueId}.name`) ||
                        !get(form, `venuesById.${venueId}.adress`)
                  }
                  className="button is-primary is-medium"
                  method={method}
                  path={submitPath}
                  storeKey="venues"
                  text="Enregistrer"
                />
              </div>
              <div className="control">
                <NavLink
                  className="button is-primary is-outlined is-medium"
                  to={`/${collectionToPath('venues')}`} >
                  Retour
                </NavLink>
              </div>
            </div>
          </form>
        </div>
      </div>
    </PageWrapper>
  )
}
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => Object.assign(
      { user: state.user },
      selectCurrentOfferer(state, ownProps)
    ),
    { requestData, resetForm }
  )
)(OffererPage)
