import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import ProviderManager from '../ProviderManager'
import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import { resetForm } from '../../reducers/form'
import SubmitButton from '../layout/SubmitButton'
import selectCurrentVenue from '../../selectors/currentVenue'
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
        `offerers/${offererId}`,
        {
          key: 'offerers'
        }
      )
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
      match: { params },
      venue
    } = nextProps
    const isNew = params.venueId === 'nouveau'
    const venueId = isNew ? NEW : venueId
    return {
      apiPath: isNew ? `venues` : `venues/${venueId}`,
      isLoading: !(get(venue, 'id') || isNew),
      isNew,
      method: isNew ? 'POST' : 'PATCH',
      venueId
    }
  }

  render () {
    const {
      match: {
        params: {
          offererId
        }
      },
      offerer,
      venue,
    } = this.props

    const {
      address,
      city,
      name,
      postalCode,
      siret,
      venueProviders
    } = venue || {}

    const {
      apiPath,
      isLoading,
      isNew,
      method,
      venueId
    } = this.state

    console.log('isNew', isNew)

    return (
      <PageWrapper name='offerer' loading={isLoading}>

        <h1 className='title has-text-centered level-left'>
          {get(offerer, 'name')}
        </h1>

        <h1 className='is-size-1 has-text-grey is-italic level-left'>
          {isNew ? 'Créer un' : 'Modifier le'} lieu
        </h1>

        <p className='subtitle'>
          Ajoutez un lieu où trouver vos offres
        </p>
        <p className='small has-text-grey'>
          Les champs marqués d'un <span> * </span> sont obligatoires
        </p>

        <br />
        <br />
        <FormField
          autoComplete="siret"
          className='is-rounded'
          controlClassName='columns'
          collectionName="venues"
          defaultValue={siret}
          entityId={venueId}
          inputClassName='column is-3 aligned'
          label={<Label title="SIRET:" />}
          labelClassName='column is-3'
          name="siret"
          type="sirene"
          sireType="siret"
        />
        <FormField
          autoComplete="name"
          className='is-rounded'
          collectionName="venues"
          controlClassName='columns'
          defaultValue={name}
          entityId={venueId}
          inputClassName='column aligned'
          label={<Label title="Nom du lieu:" />}
          labelClassName='column is-3'
          name="name"
        />

        <br />
        <div className="columns">
          <p className="column"> <b> ADRESSE </b> </p>
        </div>
        <FormField
          autoComplete="address"
          className='input is-rounded'
          collectionName="venues"
          controlClassName='columns'
          defaultValue={address || ''}
          entityId={venueId}
          inputClassName='column aligned'
          label={<Label title="Numéro et voie :*" />}
          labelClassName='column is-3'
          name="address"
          type="address"
        />
        <FormField
          autoComplete="postalCode"
          className='input is-rounded'
          collectionName="venues"
          controlClassName='columns'
          defaultValue={postalCode || ''}
          entityId={venueId}
          inputClassName='column is-2 mt1'
          label={<Label title="Code Postal:*" />}
          labelClassName='column is-3'
          name="postalCode"
        />
        <FormField
          autoComplete="city"
          className='input is-rounded'
          collectionName="venues"
          controlClassName='columns'
          defaultValue={city || ''}
          entityId={venueId}
          inputClassName='column is-5 mt1'
          label={<Label title="Ville:*" />}
          labelClassName='column is-3'
          name="city"
        />

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
                        managingOffererId: offererId
                      },
                      get(form, `venuesById.${venueId}`)
                    )
                  }
                  getIsDisabled={form =>
                    isNew
                      ? !get(form, `venuesById.${venueId}.name`) ||
                        !get(form, `venuesById.${venueId}.address`) ||
                        !get(form, `venuesById.${venueId}.postalCode`)
                      : !get(form, `venuesById.${venueId}.name`) &&
                        !get(form, `venuesById.${venueId}.address`) &&
                        !get(form, `venuesById.${venueId}.postalCode`)
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

      {
        !isNew && [
          <br key={0}/>,
          <ProviderManager key={1} venueProviders={venueProviders} />
        ]
      }

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
