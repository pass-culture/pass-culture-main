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
import { addBlockers, removeBlockers } from '../../reducers/blockers'
import { closeNotification, showNotification } from '../../reducers/notification'
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
          normalizer: {
            eventOccurences: {
              key: 'eventOccurences',
              normalizer: {
                event: 'occasions'
              }
            }
          }
        }
      )
    }
  }

  handleSuccessData = (state, action) => {
    const {
      addBlockers,
      closeNotification,
      history,
      offerer,
      removeBlockers,
      showNotification
    } = this.props
    const venueId = get(action, 'data.id')
    if (!venueId) {
      console.warn('You should have a venueId here')
      return
    }
    // const redirectPathname = `/structures/${offerer.id}`
    const redirectPathname = `/structures/${offerer.id}/lieux/${venueId}`
    history.push(redirectPathname)
    showNotification({
      text: "Lieu ajouté avec succès !",
      type: 'success'
    })
    addBlockers(
      'venue-notification',
      ({ location: { pathname }}) => {
        if (pathname === redirectPathname) {
          removeBlockers('venue-notification')
          closeNotification()
        }
      }
    )
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      match: { params: { venueId } },
      venue
    } = nextProps
    const isNew = venueId === 'nouveau'
    const venueIdOrNew = isNew ? NEW : venueId
    return {
      apiPath: isNew ? `venues` : `venues/${venueId}`,
      isLoading: !(get(venue, 'id') || isNew),
      isNew,
      method: isNew ? 'POST' : 'PATCH',
      venueIdOrNew
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
      venueIdOrNew
    } = this.state
    return (
      <PageWrapper name='offerer' loading={isLoading} backTo={{label: 'Structure', path: `/structures/${get(offerer, 'id')}`}}>
        <div className='section'>
          <h2 className='subtitle has-text-weight-bold'>
            {get(venue, 'name')}
          </h2>

          <h1 className='pc-title'>
            {isNew ? 'Créer un' : 'Modifier le'} lieu
          </h1>
        </div>

        {!isNew && <ProviderManager venueProviders={venueProviders} />}

        <div className='section'>
          <h2 className='pc-list-title'>
            IDENTIFIANTS
            <span className='is-pulled-right is-size-7 has-text-grey'>
              Les champs marqués d'un <span className='required-legend'> * </span> sont obligatoires
            </span>
          </h2>
          <FormField
            collectionName="venues"
            defaultValue={siret}
            entityId={venueIdOrNew}
            label={<Label title="SIRET :" />}
            name="siret"
            type="sirene"
            sireType="siret"
            isHorizontal
          />
          <FormField
            collectionName="venues"
            defaultValue={name}
            entityId={venueIdOrNew}
            label={<Label title="Nom du lieu :" />}
            name="name"
            isHorizontal
            isExpanded
          />
        </div>
        <div className='section'>
          <h2 className='pc-list-title'>
            ADRESSE
          </h2>
          <FormField
            autoComplete="address"
            collectionName="venues"
            defaultValue={address || ''}
            entityId={venueIdOrNew}
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
            entityId={venueIdOrNew}
            label={<Label title="Code Postal :" />}
            name="postalCode"
            isHorizontal
            required
          />
          <FormField
            autoComplete="city"
            collectionName="venues"
            defaultValue={city || ''}
            entityId={venueIdOrNew}
            label={<Label title="Ville :" />}
            name="city"
            isHorizontal
            required
          />
        </div>

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
                    get(form, `venuesById.${venueIdOrNew}`)
                  )
                }
                getIsDisabled={form =>
                  isNew
                    ? !get(form, `venuesById.${venueIdOrNew}.name`) ||
                      !get(form, `venuesById.${venueIdOrNew}.address`) ||
                      !get(form, `venuesById.${venueIdOrNew}.postalCode`)
                    : !get(form, `venuesById.${venueIdOrNew}.name`) &&
                      !get(form, `venuesById.${venueIdOrNew}.address`) &&
                      !get(form, `venuesById.${venueIdOrNew}.postalCode`)
                }
                className="button is-primary is-medium"
                handleSuccess={this.handleSuccessData}
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
    {
      addBlockers,
      closeNotification,
      resetForm,
      removeBlockers,
      showNotification
    })
)(VenuePage)
