import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'

import ProviderManager from '../ProviderManager'
import FormField from '../layout/FormField'
import Icon from '../layout/Icon'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { requestData } from '../../reducers/data'
import { resetForm } from '../../reducers/form'
import { addBlockers, removeBlockers } from '../../reducers/blockers'
import { closeNotification, showNotification } from '../../reducers/notification'
import offererSelector from '../../selectors/offerer'
import venueSelector from '../../selectors/venue'
import { NEW } from '../../utils/config'

import Form from '../layout/Form'
import Field from '../layout/Field'
import Submit from '../layout/Submit'

class VenuePage extends Component {

  constructor () {
    super()
    this.state = {
      isEdit: false,
      isLoading: false,
      isNew: false,
      isReadOnly: true
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      location: { search },
      match: { params: { offererId, venueId } },
      offerer,
      venue
    } = nextProps
    const isEdit = search === '?modifie'
    const isNew = venueId === 'nouveau'
    const isReadOnly = !isNew && !isEdit
    const venueIdOrNew = isNew ? NEW : venueId
    const offererName = get(offerer, 'name')
    const routePath = `/structures/${offererId}`
    const venueName = get(venue, 'name')
    return {
      apiPath: isNew ? `venues` : `venues/${venueId}`,
      isLoading: !(get(offerer, 'id') && (get(venue, 'id') || isNew)),
      isNew,
      method: isNew ? 'POST' : 'PATCH',
      isEdit,
      isReadOnly,
      offererName,
      routePath,
      venueIdOrNew,
      venueName
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match: { params: { offererId, venueId } },
      requestData,
      user
    } = this.props
    if (user) {
      requestData(
        'GET',
        `offerers/${offererId}`,
        {
          handleSuccess,
          handleFail,
          key: 'offerers'
        }
      )
      venueId !== 'nouveau' && requestData(
        'GET',
        `offerers/${offererId}/venues/${venueId}`,
        {
          handleSuccess,
          handleFail,
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

  handleSuccess = (state, action) => {
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
    const redirectPathname = get(action, 'method') === 'POST'
      ? `/structures/${offerer.id}/lieux/${venueId}`
      : `/structures/${offerer.id}`
    history.push(redirectPathname)
    showNotification({
      text: get(action, 'method') === 'POST'
        ? "Lieu ajouté avec succès !"
        : "Lieu modifié avec succès !",
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

  componentWillUnmount() {
    this.props.resetForm()
  }

  render () {
    const {
      match: {
        params: { offererId }
      },
      location: {
        pathname
      },
      offerer,
      user,
      venue,
    } = this.props

    const {
      address,
      city,
      name,
      postalCode,
      siret,
      bookingEmail,
      latitude,
      longitude,
    } = venue || {}

    const {
      apiPath,
      offererName,
      isNew,
      isReadOnly,
      method,
      routePath,
      venueIdOrNew,
      venueName
    } = this.state

    const formData = Object.assign({}, venue, {managingOffererId: offererId, bookingEmail: get(user, 'email')})

    return (
      <PageWrapper
        backTo={{
          label: offererName === venueName
            ? 'STRUCTURE'
            : offererName,
          path: routePath
        }}
        name='venue'
        handleDataRequest={this.handleDataRequest}
      >
        <div className='section hero'>
          <h2 className='subtitle has-text-weight-bold'>
            {get(venue, 'name')}
          </h2>

          <h1 className='pc-title'>
            Lieu
          </h1>

          {
            isNew && (
              <p className="subtitle">
                Ajoutez un lieu où accéder à vos offres.
              </p>
            )
          }

          {
            get(offerer, 'id') && get(venue, 'id') && (
              <NavLink to={`/offres/nouveau?lieu=${venue.id}`}
                className='button is-primary is-medium is-pulled-right cta'>
                <span className='icon'><Icon svg='ico-offres-w' /></span>
                <span>Créer une offre</span>
              </NavLink>
            )
          }
        </div>

        {!isNew && <ProviderManager venue={venue} />}

        <Form name='venue' handleSuccess={this.handleSuccess} action={`/venues/${get(venue, 'id', '')}`} data={formData}>
          <Field type='hidden' name='managingOffererId' />
          <div className='section'>
            <h2 className='pc-list-title'>
              IDENTIFIANTS
              <span className='is-pulled-right is-size-7 has-text-grey'>
                Les champs marqués d'un <span className='required-legend'> * </span> sont obligatoires
              </span>
            </h2>
            <div className='field-group'>
              <Field name='siret' label='SIRET' readOnly={isReadOnly} required />
              <Field name='name' label='Nom du lieu' readOnly={isReadOnly} required />
              <Field type='email' name='bookingEmail' label='E-mail' readOnly={isReadOnly} required />
            </div>
          </div>
          <div className='section'>
            <h2 className='pc-list-title'>
              ADRESSE
            </h2>
            <div className='field-group'>
              <Field type="geo" name='address' label='Numéro et voie' readOnly={isReadOnly} required isExpanded />
              <Field name='postalCode' label='Code postal' readOnly={isReadOnly} required />
              <Field name='city' label='Ville' readOnly={isReadOnly} required />
            </div>
          </div>

        <hr />
        <div className="field is-grouped is-grouped-centered"
          style={{justifyContent: 'space-between'}}>
          <div className="control">
            {
              isReadOnly
                ? (
                  <NavLink to={`${pathname}?modifie`} className='button is-secondary is-medium'>
                    Modifier le lieu
                  </NavLink>
                )
                : (
                  <NavLink
                    className="button is-secondary is-medium"
                    to={`/structures/${offererId}`}>
                    Annuler
                  </NavLink>
                )
            }
          </div>
          <div className="control">
            <div className="field is-grouped is-grouped-centered"
              style={{justifyContent: 'space-between'}}>
              <div className="control">
                {
                  isReadOnly
                    ? (
                      <NavLink to={routePath} className='button is-primary is-medium'>
                        Terminer
                      </NavLink>
                    )
                    : (
                      <Submit className="button is-primary is-medium">{isNew ? 'Créer' : 'Valider'}</Submit>
                    )
                }
              </div>
            </div>
          </div>
        </div>
      </Form>
    </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      user: state.user,
      venue: venueSelector(state, ownProps.match.params.venueId),
      offerer: offererSelector(state, ownProps.match.params.offererId),
    }),
    {
      addBlockers,
      closeNotification,
      resetForm,
      removeBlockers,
      requestData,
      showNotification
    })
)(VenuePage)
