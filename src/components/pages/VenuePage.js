import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import ProviderManager from '../ProviderManager'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import { resetForm } from '../../reducers/form'
import SubmitButton from '../layout/SubmitButton'
import selectCurrentVenue from '../../selectors/currentVenue'
import selectCurrentOfferer from '../../selectors/currentOfferer'
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

  componentDidMount () {
    this.handleRequestData()
  }

  componentDidUpdate (prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleRequestData()
    }
  }

  componentWillUnmount() {
    this.props.resetForm()
  }

  handleRequestData =() => {
    const {
      match: { params: { offererId } },
      requestData,
      user
    } = this.props
    if (user) {
      requestData(
        'GET',
        `offerers/${offererId}/venues`,
        {
          key: 'venues',
          isMergingArray: false
        }
      )
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      match: { params: { offererId, venueId } },
      venue
    } = nextProps
    const isNew = venueId === 'nouveau'
    const isLoading = !(get(venue, 'id') || isNew)
    const method = isNew ? 'POST' : 'PATCH'
    return {
      apiPath: isNew ? `venues/` : `venues/${venueId}`,
      isLoading,
      isNew,
      method
    }
  }

  render () {
    const {
      match: {
        params: {
          offererId,
          venueId
        }
      },
      offerer,
      venue,
    } = this.props

    const {
      address,
      city,
      name,
      siret,
      departementCode,
      venueProviders
    } = venue || {}

    const {
      apiPath,
      isLoading,
      isNew,
      method,
    } = this.state

    return (
      <PageWrapper name='offerer' loading={isLoading}>

        <h1 className='title has-text-centered'>{get(offerer, 'name')}</h1>
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

        <br />
        <ProviderManager venueProviders={venueProviders} />

        <br />
        <div className="field is-grouped is-grouped-centered"
          style={{justifyContent: 'space-between'}}>
          <div className="control">

            <div className="field is-grouped is-grouped-centered"
              style={{justifyContent: 'space-between'}}>
              <div className="control">
                <SubmitButton
                  getBody={form => Object.assign(
                      {
                        managingOffererId: offererId,
                        venueProviders: get(form, `venueProvidersById`)
                          && Object.values(get(form, `venueProvidersById`))
                      },
                      get(form, `venuesById.${venueId}`)
                    )
                  }
                  getIsDisabled={form =>
                    isNew
                      ? !get(form, `venuesById.${venueId}.name`) ||
                        !get(form, `venuesById.${venueId}.address`)
                      : !get(form, `venuesById.${venueId}.name`) &&
                        !get(form, `venuesById.${venueId}.address`) &
                        (
                          !get(form, `venueProvidersById`) ||
                          Object.keys(get(form, `venueProvidersById`)) === 0
                        )
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
    (state, ownProps) => ({
      user: state.user,
      venue: selectCurrentVenue(state, ownProps),
      offerer: selectCurrentOfferer(state, ownProps),
    }),
    { resetForm })
)(VenuePage)
