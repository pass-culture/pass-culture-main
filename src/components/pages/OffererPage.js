import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import Icon from '../layout/Icon'
import Label from '../layout/Label'
import VenuesList from '../VenuesList'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
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
    } = this.props

    const {
      address,
      bookingEmail,
      name,
      siren,
    } = currentOfferer || {}

    const {
      apiPath,
      isLoading,
      isNew,
      method,
      offererIdOrNew,
    } = this.state

    const notification = search === '?success=true' && {
      text: "L' ajout du lieu a bien été prise en compte",
      type: 'success'
    }

    return (
      <PageWrapper
        backTo={{label: 'Vos structures', path: '/structures'}}
        loading={isLoading}
        name='offerer'
        notification={notification}
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
          {isNew && (
            <div>
              <FormField
                autoComplete="email"
                collectionName="offerers"
                defaultValue={bookingEmail || ''}
                entityId={offererIdOrNew}
                label={<Label title="Email de réservation :" />}
                name="bookingEmail"
                isHorizontal
              />
            </div>
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
                  getBody={form => form.offerersById[offererIdOrNew]}
                  getIsDisabled={form => {
                    return isNew
                      ? !get(form, `offerersById.${offererIdOrNew}.name`) ||
                        !get(form, `offerersById.${offererIdOrNew}.address`)
                      : !get(form, `offerersById.${offererIdOrNew}.name`) &&
                        !get(form, `offerersById.${offererIdOrNew}.address`)
                  }

                  }
                  className="button is-primary is-medium"
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
    { resetForm }
  )
)(OffererPage)
