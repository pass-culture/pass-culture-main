import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import { resetForm } from '../../reducers/form'
import SubmitButton from '../layout/SubmitButton'
import selectCurrentVenue from '../../selectors/currentVenue'
import withLogin from '../hocs/withLogin'

import { NEW } from '../../utils/config'


class VenuePage extends Component {

  constructor () {
    super()
    this.state = {
      isLoading: false,
      isNew: false
    }
  }

  componentWillUnmount() {
    this.props.resetForm()
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      id,
      match: { params },
    } = nextProps
    const isNew = params.venueId === 'nouveau'
    const isLoading = !(id || isNew)
    const method = isNew ? 'POST' : 'PATCH'
    return {
      apiPath: isNew ? `venues/` : `venues/${id}`,
      isLoading,
      isNew,
      method,
      offererId: isNew ? NEW : id
    }
  }

  render () {
    const {
      address,
      name,
      siret,
      match: { params: {
        offererId,
        venueId
      } },
      departementCode,
      city
    } = this.props
    const {
      apiPath,
      isLoading,
      isNew,
      method,
    } = this.state

    return (
      <PageWrapper name='offerer' loading={isLoading}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
            </div>

            <h1 className='title has-text-centered'>STRUCTURE : A FAIRE !!!!!!! </h1>
            <h1 className='title has-text-centered'>{isNew ? 'Créer' : 'Modifier'} un lieu</h1>
            <FormField
              autoComplete="siret"
              collectionName="venues"
              defaultValue={siret}
              entityId={venueId}
              label={<Label title="Siret" />}
              name="siret"
              type="sirene"
              sireType="siret"
            />
            <FormField
              autoComplete="name"
              collectionName="venues"
              defaultValue={name}
              entityId={venueId}
              label={<Label title="Nom" />}
              name="name"
            />
            <FormField
              autoComplete="address"
              collectionName="venues"
              defaultValue={address || ''}
              entityId={venueId}
              label={<Label title="Numéro et voie :*" />}
              name="address"
              type="address"
            />
            <FormField
              autoComplete="departementCode"
              collectionName="venues"
              defaultValue={departementCode || ''}
              entityId={venueId}
              label={<Label title="Code Postal" />}
              name="departementCode"
            />
            <FormField
              autoComplete="city"
              collectionName="venues"
              defaultValue={city || ''}
              entityId={venueId}
              label={<Label title="Ville" />}
              name="city"
            />
            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                <SubmitButton
                  getBody={form => Object.assign({ managingOffererId: offererId }, form.venuesById[venueId])}
                  getIsDisabled={form =>
                    isNew
                      ? !get(form, `venuesById.${venueId}.name`) &&
                        !get(form, `venuesById.${venueId}.address`)
                      : !get(form, `venuesById.${venueId}.name`) ||
                        !get(form, `venuesById.${venueId}.address`)
                  }
                  className="button is-primary is-medium"
                  method={method}
                  path={apiPath}
                  storeKey="venues"
                  text="Enregistrer"
                />
              </div>
              <div className="control">
                <NavLink
                  className="button is-primary is-outlined is-medium"
                  to={`/structures/${offererId}`}>
                  Retour
                </NavLink>
              </div>
            </div>
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
      selectCurrentVenue(state, ownProps)
    ),
    { resetForm })
)(VenuePage)
