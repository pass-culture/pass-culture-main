import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import ProviderManager from '../ProviderManager'
import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import Icon from '../layout/Icon'
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
      isEdit: false,
      isLoading: false,
      isNew: false,
      isReadOnly: true
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

  static getDerivedStateFromProps (nextProps) {
    const {
      location: { search },
      match: { params: { venueId } },
      offerer,
      venue
    } = nextProps
    const isEdit = search === '?modifie'
    const isNew = venueId === 'nouveau'
    const isReadOnly = !isNew && !isEdit
    const venueIdOrNew = isNew ? NEW : venueId
    const offererName = get(offerer, 'name')
    const routePath = `/structures/${get(offerer, 'id')}`
    const venueName = get(venue, 'name')
    return {
      apiPath: isNew ? `venues` : `venues/${venueId}`,
      isLoading: !(get(venue, 'id') || isNew),
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

  render () {
    const {
      location: {
        pathname
      },
      match: {
        params: {
          offererId
        }
      },
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
      offererName,
      isLoading,
      isNew,
      isReadOnly,
      method,
      routePath,
      venueIdOrNew,
      venueName
    } = this.state

    return (
      <PageWrapper
        backTo={{
          label: offererName === venueName
            ? 'STRUCTURE'
            : offererName,
          path: routePath
        }}
        name='venue'
        loading={isLoading}
      >
        <div className='section hero'>
          <h2 className='subtitle has-text-weight-bold'>
            {get(venue, 'name')}
          </h2>

          <h1 className='pc-title'>
            Lieu
          </h1>

          {
            !isNew && (
              <NavLink to={'/offres/nouveau'}
                className='button is-primary is-medium is-pulled-right cta'>
                <span className='icon'><Icon svg='ico-offres-w' /></span>
                <span>Créer une offre</span>
              </NavLink>
            )
          }
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
            isHorizontal
            label={<Label title="SIRET :" />}
            name="siret"
            readOnly={isReadOnly}
            sireType="siret"
            type="sirene"
          />
          <FormField
            collectionName="venues"
            defaultValue={name}
            entityId={venueIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Nom du lieu :" />}
            name="name"
            readOnly={isReadOnly}
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
            isHorizontal
            isExpanded
            label={<Label title="Numéro et voie :" />}
            name="address"
            readOnly={isReadOnly}
            required={!isReadOnly}
            type="address"
          />
          <FormField
            autoComplete="postalCode"
            collectionName="venues"
            defaultValue={postalCode || ''}
            entityId={venueIdOrNew}
            isHorizontal
            label={<Label title="Code Postal :" />}
            name="postalCode"
            readOnly={isReadOnly}
            required={!isReadOnly}
          />
          <FormField
            autoComplete="city"
            collectionName="venues"
            defaultValue={city || ''}
            entityId={venueIdOrNew}
            isHorizontal
            label={<Label title="Ville :" />}
            name="city"
            readOnly={isReadOnly}
            required={!isReadOnly}
          />
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
                    <SubmitButton
                      className="button is-primary is-medium"
                      getBody={form => Object.assign(
                          {
                            managingOffererId: offererId
                          },
                          get(form, `venuesById.${venueIdOrNew}`)
                        )
                      }
                      handleSuccess={this.handleSuccessData}
                      method={method}
                      path={apiPath}
                      storeKey="venues"
                      text={isNew ? "Créer" : "Valider"}
                    />
                  )
              }
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
      offerer: selectCurrentOfferer(state, ownProps)
    }),
    {
      addBlockers,
      closeNotification,
      resetForm,
      removeBlockers,
      showNotification
    })
)(VenuePage)
