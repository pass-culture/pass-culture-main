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

  static getDerivedStateFromProps (nextProps) {
    const {
      offerer,
      match: { params },
    } = nextProps
    const isNew = params.offererId === 'nouveau'
    const isLoading = !(get(offerer, 'id') || isNew)
    const method = isNew ? 'POST' : 'PATCH'
    return {
      apiPath: isNew ? `offerers/` : `offerers/${get(offerer, 'id')}`,
      isLoading,
      isNew,
      method,
      offererId: isNew ? NEW : get(offerer, 'id')
    }
  }

  handleRequestData () {
    const {
      match: { params: { offererId } },
      requestData
    } = this.props
    if (offererId !== 'nouveau') {
      requestData('GET', `offerers/${offererId}`, { key: 'offerers' })
    }
  }

  onAddProviderClick = () => {
    this.setState({ isNewProvider: true })
  }

  render () {
    const {
      offerer
    } = this.props

    const {
      address,
      bookingEmail,
      name,
      siren,
    } = offerer || {}

    const {
      apiPath,
      isLoading,
      isNew,
      method,
      offererId,
    } = this.state

    return (
      <PageWrapper name='offerer' loading={isLoading}>
        <div className='section'>
          <h1 className="pc-title">Structure</h1>
          <p className="subtitle">Détails de la structure rattachée, des lieux et des fournisseurs de ses offres.</p>
          <FormField
            autoComplete="siren"
            collectionName="offerers"
            defaultValue={siren}
            entityId={offererId}
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
            entityId={offererId}
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
            entityId={offererId}
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
                entityId={offererId}
                label={<Label title="Email de réservation :" />}
                name="bookingEmail"
                isHorizontal
              />
            </div>
          )}
        </div>
        {!isNew && (
          <div className='section'>
            <h2 className='pc-second-title'>
              Lieux
            </h2>
            <VenuesList />
            <div className='has-text-right'>
              <NavLink to={`/structures/${offererId}/lieux/nouveau`}
                className="button is-secondary is-outlined">
                + Ajouter un lieu
              </NavLink>
            </div>
          </div>
        )}
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
            getBody={form => form.offerersById[offererId]}
            getIsDisabled={form => {
              return isNew
                ? !get(form, `offerersById.${offererId}.name`) ||
                  !get(form, `offerersById.${offererId}.address`)
                : !get(form, `offerersById.${offererId}.name`) &&
                  !get(form, `offerersById.${offererId}.address`)
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
    </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      offerer: selectCurrentOfferer(state, ownProps),
    }),
    { resetForm }
  )
)(OffererPage)
