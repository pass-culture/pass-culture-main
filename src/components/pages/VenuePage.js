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
import { SUCCESS } from '../../reducers/queries'
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

  handleRequestData = () => {
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

  handleSubmitStatusChange = status => {
    const {
      history,
      offerer
    } = this.props
    if (status === SUCCESS) {
      history.push(`/structures/${offerer.id}?success=true`)
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
    return (
      <PageWrapper name='offerer' loading={isLoading} backTo={{label: 'Structure', path: `/structures/${get(offerer, 'id')}`}}>
        <div className='section'>
          <h2 className='subtitle has-text-weight-bold'>
            {get(offerer, 'name')}
          </h2>

          <h1 className='pc-title'>
            {isNew ? 'Créer un' : 'Modifier le'} lieu
          </h1>

          <p className='subtitle'>
            Ajoutez un lieu où trouver vos offres
            <br />
            <span className='is-size-7 has-text-grey'>
              Les champs marqués d'un <span className='required-legend'> * </span> sont obligatoires
            </span>
          </p>
        </div>
        <div className='section'>
          <FormField
            collectionName="venues"
            defaultValue={siret}
            entityId={venueId}
            label={<Label title="SIRET :" />}
            name="siret"
            type="sirene"
            sireType="siret"
            isHorizontal
          />
          <FormField
            collectionName="venues"
            defaultValue={name}
            entityId={venueId}
            label={<Label title="Nom du lieu :" />}
            name="name"
            isHorizontal
            isExpanded
          />
        </div>
        <div className='section'>
          <h4 className='pc-form-section'>Adresse</h4>

          <FormField
            autoComplete="address"
            collectionName="venues"
            defaultValue={address || ''}
            entityId={venueId}
            label={<Label title="Numéro et voie :" />}
            name="address"
            type="address"
            isHorizontal
            isExpanded
            required
          />
          <FormField
            autoComplete="postalCode"
            collectionName="venues"
            defaultValue={postalCode || ''}
            entityId={venueId}
            label={<Label title="Code Postal :" />}
            name="postalCode"
            isHorizontal
            required
          />
          <FormField
            autoComplete="city"
            collectionName="venues"
            defaultValue={city || ''}
            entityId={venueId}
            label={<Label title="Ville :" />}
            name="city"
            isHorizontal
            required
          />
        </div>

      {!isNew && <ProviderManager venueProviders={venueProviders} />}
      <hr />
      <div className="field is-grouped is-grouped-centered"
        style={{justifyContent: 'space-between'}}>
        <div className="control">
          <NavLink
            className="button is-secondary is-medium"
            to={`/structures/${offererId}`}>
            Retour
          </NavLink>
        </div>
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
                handleStatusChange={this.handleSubmitStatusChange}
                method={method}
                path={apiPath}
                storeKey="venues"
                text="Valider"
              />
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
