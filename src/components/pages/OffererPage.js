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
import { closeNotification, showNotification } from '../../reducers/notification'
import { resetForm } from '../../reducers/form'
import selectOfferer from '../../selectors/offerer'
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
      offerer,
      match: { params },
    } = nextProps
    const offererId = get(offerer, 'id')
    const isNew = params.offererId === 'nouveau'
    const isLoading = !(offererId || isNew)
    const method = isNew ? 'POST' : 'PATCH'
    return {
      apiPath: isNew ? `offerers/` : `offerers/${offererId}`,
      isLoading,
      isNew,
      method,
      offererIdOrNew: isNew ? NEW : offererId
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
      history,
      showNotification
    } = this.props
    history.push('/structures')
    showNotification({
      text: 'Votre structure a bien été enregistrée, elle est en cours de validation.',
      type: 'success'
    })
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
      offerer,
      user
    } = this.props

    const {
      address,
      bookingEmail,
      name,
      siren,
      postalCode,
      city,
    } = offerer || {}

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
        <div className='section hero'>
          <h2 className='subtitle has-text-weight-bold'>
            {name}
          </h2>
          <h1 className="pc-title">Structure</h1>
          <p className="subtitle">
            Détails de la structure rattachée, des lieux et des fournisseurs de ses offres.
          </p>
        </div>

        <div className='section'>
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
              LIEUX
            </h2>
            <VenuesList />
            <div className='has-text-centered'>
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
      offerer: selectOfferer(state, ownProps),
    }),
    {
      closeNotification,
      resetForm,
      showNotification
    }
  )
)(OffererPage)
