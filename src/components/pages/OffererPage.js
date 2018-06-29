import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'

import VenueItem from '../VenueItem'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { requestData } from '../../reducers/data'
import { closeNotification, showNotification } from '../../reducers/notification'
import { resetForm } from '../../reducers/form'
import createOffererSelector from '../../selectors/createOfferer'
import createOfferersSelector from '../../selectors/createOfferers'
import createVenuesSelector from '../../selectors/createVenues'
import { NEW } from '../../utils/config'
import { offererNormalizer } from '../../utils/normalizers'


class OffererPage extends Component {

  constructor () {
    super()
    this.state = {
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
    const method = isNew ? 'POST' : 'PATCH'
    return {
      apiPath: isNew ? `offerers/` : `offerers/${offererId}`,
      isNew,
      method,
      offererIdOrNew: isNew ? NEW : offererId
    }
  }



  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match: { params: { offererId } },
      requestData,
    } = this.props
    const { isNew } = this.state
    !isNew && requestData(
      'GET',
      `offerers/${offererId}`,
      {
        handleSuccess,
        handleFail,
        key: 'offerers',
        normalizer: offererNormalizer
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

  componentWillUnmount() {
    this.props.resetForm()
  }


  render () {
    console.log('state -------------------', this.state)

    const {
      offerer,
      user,
      venues,
      fetchedName,
    } = this.props

    const {
      address,
      name,
      siren,
      postalCode,
      city,
    } = offerer || {}

    const {
      apiPath,
      isNew,
      method,
      offererIdOrNew,
    } = this.state

    return (
      <PageWrapper
        backTo={{label: 'Vos structures', path: '/structures'}}
        name='offerer'
        handleDataRequest={this.handleDataRequest}
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
            required
          />

          {isNew && fetchedName &&
            <div>
              <FormField
                autoComplete="name"
                collectionName="offerers"
                defaultValue={name || ''}
                entityId={offererIdOrNew}
                label={<Label title="Désignation:" />}
                name="name"
                type="name"
                isHorizontal
                isExpanded
                readOnly={isNew}
              />
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
                readOnly={isNew}
              />
              <FormField
                autoComplete="postalCode"
                collectionName="offerers"
                defaultValue={postalCode || ''}
                entityId={offererIdOrNew}
                label={<Label title="Code Postal :" />}
                name="postalCode"
                isHorizontal
                readOnly={isNew}
              />
              <FormField
                autoComplete="city"
                collectionName="offerers"
                defaultValue={city || ''}
                entityId={offererIdOrNew}
                label={<Label title="Ville :" />}
                name="city"
                isHorizontal
                readOnly={isNew}
              />
              <FormField
                autoComplete="email"
                collectionName="offerers"
                defaultValue={get(user, 'email', '')}
                entityId={offererIdOrNew}
                label={<Label title="Email de réservation :" />}
                name="bookingEmail"
                isHorizontal
              />
            </div>
          }
          { !isNew &&
            ([
              <FormField
                autoComplete="name"
                collectionName="offerers"
                defaultValue={name || ''}
                entityId={offererIdOrNew}
                key={0}
                label={<Label title="Désignation :" />}
                name="name"
                type="name"
                readOnly={!isNew}
                isHorizontal
                isExpanded
              />,
              <FormField
                autoComplete="address"
                collectionName="offerers"
                defaultValue={address || ''}
                entityId={offererIdOrNew}
                key={1}
                label={<Label title="Siège social :" />}
                name="address"
                type="adress"
                readOnly={!isNew}
                isHorizontal
                isExpanded
              />
            ])
          }
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
            <ul className='pc-list venues-list'>
              {
                venues.map(v =>
                  <VenueItem key={v.id} venue={v} />)
              }
            </ul>
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

const offerersSelector = createOfferersSelector()
const offererSelector = createOffererSelector(offerersSelector)
const venuesSelector = createVenuesSelector()

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const offererId = ownProps.match.params.offererId
      const offerer = offererSelector(state, offererId)
      const fetchedName = get(offerer, 'name') || get(state,   `form.offerersById.${NEW}.name`)
      return {
        offerer: offererSelector(state, offererId),
        venues: venuesSelector(state, offererId),
        user: state.user,
        fetchedName
      }
    },
    {
      closeNotification,
      requestData,
      resetForm,
      showNotification
    }
  )
)(OffererPage)
