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
      id,
      match: { params },
    } = nextProps
    const isNew = params.offererId === 'nouveau'
    const isLoading = !(id || isNew)
    const method = isNew ? 'POST' : 'PATCH'
    return {
      apiPath: isNew ? `offerers/` : `offerers/${id}`,
      isLoading,
      isNew,
      method,
      offererId: isNew ? NEW : id
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
    console.log('OUAI')
    this.setState({ isNewProvider: true })
  }

  render () {
    const {
      address,
      bookingEmail,
      name,
      providers,
      siren,
      venues
    } = this.props
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
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to='/structures'
                className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>

            <br/>
            <h1 className='title has-text-centered'>
              {isNew ? 'Créer' : 'Modifier'} une structure
            </h1>
            <FormField
              autoComplete="siren"
              collectionName="offerers"
              defaultValue={siren}
              entityId={offererId}
              label={<Label title="Siren" />}
              name="siren"
              type="sirene"
              sireType="siren"
            />
            <FormField
              autoComplete="name"
              collectionName="offerers"
              defaultValue={name}
              entityId={offererId}
              label={<Label title="Nom" />}
              name="name"
            />
            <FormField
              autoComplete="address"
              collectionName="offerers"
              defaultValue={address || ''}
              entityId={offererId}
              label={<Label title="Adresse" />}
              name="address"
              type="adress"
            />
            <FormField
              autoComplete="email"
              collectionName="offerers"
              defaultValue={bookingEmail || ''}
              entityId={offererId}
              label={<Label title="Email de réservation" />}
              name="bookingEmail"
            />
            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
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
              <div className="control">
                <NavLink
                  className="button is-primary is-outlined is-medium"
                  to='/structures' >
                  Retour
                </NavLink>
              </div>
            </div>

            <br/>
            <h2 className='subtitle is-2' key={0}>
              Mes lieux
            </h2>
            <NavLink to={`/structures/${offererId}/lieux/nouveau`}
              className="button is-primary is-outlined">
              Nouveau lieu
            </NavLink>
            <VenuesList />

        </div>
      </div>
    </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => Object.assign(
      {
        venues: state.data.venues
      },
      selectCurrentOfferer(state, ownProps)
    ),
    { resetForm }
  )
)(OffererPage)
