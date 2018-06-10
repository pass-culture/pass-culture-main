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
    requestData('GET', `offerers/${offererId}`, { key: 'offerers' })
  }

  onAddProviderClick = () => {
    this.setState({ isNewProvider: true })
  }

  render () {
    const {
      offerer,
      venues
    } = this.props

    const {
      id,
      address,
      bookingEmail,
      name,
      providers,
      siren,
    } = offerer || {}

    const {
      apiPath,
      isLoading,
      isNew,
      method,
      offererId,
      offererProviders
    } = this.state

    return (
      <PageWrapper name='offerer' loading={isLoading}>
        <div className='columns'>
          <div className='column'>
            <div className='section'>
              <h1 className="title is-size-1 is-h1 has-text-grey is-italic">Structure</h1>
              <p className="subtitle">Retrouvez ici la ou les structures dont vous gérez les offres Pass Culture.</p>
              <FormField
                autoComplete="siren"
                collectionName="offerers"
                defaultValue={siren}
                entityId={offererId}
                label={<Label title="Siren" />}
                name="siren"
                type="sirene"
                sireType="siren"
                readOnly={!isNew}
                className='input is-rounded'
              />
              <FormField
                autoComplete="name"
                collectionName="offerers"
                defaultValue={name}
                entityId={offererId}
                label={<Label title="Nom" />}
                name="name"
                className='input is-rounded'
              />
              <FormField
                autoComplete="address"
                collectionName="offerers"
                defaultValue={address || ''}
                entityId={offererId}
                label={<Label title="Adresse" />}
                name="address"
                type="adress"
                className='input is-rounded'
              />
              <FormField
                autoComplete="email"
                collectionName="offerers"
                defaultValue={bookingEmail || ''}
                entityId={offererId}
                label={<Label title="Email de réservation" />}
                name="bookingEmail"
                className='input is-rounded'
              />
            </div>
            <hr />
            <div className='section'>
              <h2 className='subtitle is-2' key={0}>
                Lieux
              </h2>
              <VenuesList />
              <div className='has-text-right'>
                <NavLink to={`/structures/${offererId}/lieux/nouveau`}
                  className="button is-primary is-outlined">
                  Nouveau lieu
                </NavLink>
              </div>
            </div>
            <hr />
            <div className='section'>
              <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
                <div className="control">
                  <NavLink
                    className="button is-primary is-outlined is-medium"
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
                    text="Enregistrer"
                  />
                </div>
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
    (state, ownProps) => (      {
      venues: state.data.venues,
      offerer: selectCurrentOfferer(state, ownProps),
    }),
    { resetForm }
  )
)(OffererPage)
