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
import { resetForm } from '../../reducers/form'
import selectCurrentOfferer from '../../selectors/currentOfferer'
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
      venueId: isNew ? NEW : id
    }
  }

  render () {
    const {
      address,
      name,
      siret,
      user,
      managingOffererId
    } = this.props
    const {
      apiPath,
      isLoading,
      isNew,
      method,
      venueId
    } = this.state
    const isSiret = true

    return (
      <PageWrapper name='offerer' loading={isLoading}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
            </div>

            <h1 className='title has-text-centered'>{isNew ? 'Créer' : 'Modifier'} un lieu</h1>
            { user && user.offerers &&
                <FormField
                  collectionName="venues"
                  defaultValue={managingOffererId || ''}
                  entityId={venueId}
                  label={<Label title="Choisissez la structure" />}
                  name="managingOffererId"
                  type="select"
                  options={(get(user, 'offerers') || []).map(o =>
                ({ label: o.name, value: o.id }))}
              />
            }

            <FormField
              autoComplete="siret"
              collectionName="venues"
              defaultValue={siret}
              entityId={venueId}
              label={<Label title="Siret" />}
              name="siret"
              type="sirene"
              isSiret={isSiret}
              // isSiren={isSiren}
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
              label={<Label title="Adresse" />}
              name="address"
              type="adress"
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
                  path={apiPath}
                  storeKey="venues"
                  text="Enregistrer"
                />
              </div>
              <div className="control">
                <NavLink
                  className="button is-primary is-outlined is-medium"
                  to='/lieux' >
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
      selectCurrentOfferer(state, ownProps)
    ),
    { resetForm }
  )
)(VenuePage)
