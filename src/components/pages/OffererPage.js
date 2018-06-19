import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import VenuesList from '../VenuesList'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { addBlockers, removeBlockers } from '../../reducers/blockers'
import { closeNotification, showNotification } from '../../reducers/notification'
import { resetForm } from '../../reducers/form'
import selectCurrentOfferer from '../../selectors/currentOfferer'
import { NEW } from '../../utils/config'


class OffererPage extends Component {

  constructor () {
    super()
    this.state = {
      isLoading: false,
      isNew: false
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      currentOfferer,
      match: { params: { offererId } },
    } = nextProps
    const currentOffererId = get(currentOfferer, 'id')
    const isNew = offererId === 'nouveau'
    const isLoading = !(currentOffererId || isNew)
    const method = isNew ? 'POST' : 'PATCH'
    return {
      apiPath: isNew ? `offerers/` : `offerers/${currentOffererId}`,
      isLoading,
      isNew,
      method,
      offererIdOrNew: isNew ? NEW : currentOffererId
    }
  }

  handleRequestData () {
    const {
      match: { params: { offererId } },
      requestData,
      user
    } = this.props
    const { isNew } = this.state
    user && !isNew && requestData(
      'GET',
      `offerers/${offererId}`,
      {
        key: 'offerers',
        normalizer: {
          managedVenues: 'venues'
        }
      }
    )
  }

  handleSuccessData = () => {
    const {
      addBlockers,
      history,
      removeBlockers,
      showNotification
    } = this.props
    const redirectPathname = '/structures'
    history.push(redirectPathname)
    showNotification({
      text: 'Votre structure a bien été enregistrée',
      type: 'success'
    })
    addBlockers(
      'offerer-notification',
      ({ location: { pathname }}) => {
        if (pathname === redirectPathname) {
          removeBlockers('offerer-notification')
          closeNotification()
        }
      }
    )
  }

  onAddProviderClick = () => {
    this.setState({ isNewProvider: true })
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

  render () {
    const {
      currentOfferer,
      location: { search },
      user
    } = this.props

    const {
      address,
      bookingEmail,
      name,
      siren,
      postalCode,
      city,
    } = currentOfferer || {}

    const {
      apiPath,
      isLoading,
      isNew,
      method,
      offererIdOrNew,
    } = this.state
    return (
      <PageWrapper
        backTo={{label: 'Vos structures', path: '/structures'}}
        loading={isLoading}
        name='offerer'
      >
        <div className='section'>
          <h1 className="pc-title">Structure</h1>
          <p className="subtitle">
            Détails de la structure rattachée, des lieux et des fournisseurs de ses offres.
          </p>
          <FormField
            autoComplete="siren"
            collectionName="offerers"
            defaultValue={siren}
            entityId={offererIdOrNew}
            label={<Label title="Siren :" />}
            name="siren"
            type="sirene"
            sireType="siren"
            readOnly={!isNew}
            isHorizontal
          />
          <FormField
            autoComplete="name"
            collectionName="offerers"
            defaultValue={name}
            entityId={offererIdOrNew}
            label={<Label title="Dénomination :" />}
            name="name"
            readOnly={!isNew}
            isHorizontal
            isExpanded
          />
          {isNew ? (
            <div>
              <FormField
                autoComplete="address"
                collectionName="offerers"
                defaultValue={address || ''}
                entityId={offererIdOrNew}
                label={<Label title="Adresse du siège social :" />}
                name="address"
                type="address"
                isHorizontal
                isExpanded
                required
              />
              <FormField
                autoComplete="postalCode"
                collectionName="offerers"
                defaultValue={postalCode || ''}
                entityId={offererIdOrNew}
                label={<Label title="Code Postal :" />}
                name="postalCode"
                isHorizontal
                required
              />
              <FormField
                autoComplete="city"
                collectionName="offerers"
                defaultValue={city || ''}
                entityId={offererIdOrNew}
                label={<Label title="Ville :" />}
                name="city"
                isHorizontal
                required
              />
              <FormField
                autoComplete="email"
                collectionName="offerers"
                defaultValue={bookingEmail || get(user, 'email')}
                entityId={offererIdOrNew}
                label={<Label title="Email de réservation :" />}
                name="bookingEmail"
                isHorizontal
              />
            </div>
          ) : (
            <FormField
              autoComplete="address"
              collectionName="offerers"
              defaultValue={address || ''}
              entityId={offererIdOrNew}
              label={<Label title="Siège social :" />}
              name="address"
              type="adress"
              readOnly={!isNew}
              isHorizontal
              isExpanded
            />
          )}
        </div>
        {isNew ? (
          <div>
            <hr />
            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                <NavLink
                  className="button is-secondary is-medium"
                  to='/structures' >
                  Retour
                </NavLink>
              </div>
              <div className="control">
                <SubmitButton
                  className="button is-primary is-medium"
                  getBody={form => form.offerersById[offererIdOrNew]}
                  getIsDisabled={form => {
                    return isNew
                      ? !get(form, `offerersById.${offererIdOrNew}.name`) ||
                        !get(form, `offerersById.${offererIdOrNew}.address`)
                      : !get(form, `offerersById.${offererIdOrNew}.name`) &&
                        !get(form, `offerersById.${offererIdOrNew}.address`)
                  }}
                  handleSuccess={this.handleSuccessData}
                  method={method}
                  path={apiPath}
                  storeKey="offerers"
                  text="Valider"
                />
              </div>
            </div>
          </div>
        ) : (
          <div className='section'>
            <h2 className='pc-list-title'>
              Lieux
            </h2>
            <VenuesList />
            <div className='has-text-right'>
              <NavLink to={`/structures/${offererIdOrNew}/lieux/nouveau`}
                className="button is-secondary is-outlined">
                + Ajouter un lieu
              </NavLink>
            </div>
          </div>
        )}
    </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      currentOfferer: selectCurrentOfferer(state, ownProps),
    }),
    {
      closeNotification,
      resetForm,
      removeBlockers,
      showNotification
    }
  )
)(OffererPage)
