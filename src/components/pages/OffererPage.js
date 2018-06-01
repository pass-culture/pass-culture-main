import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { requestData } from '../../reducers/data'
import { resetForm } from '../../reducers/form'
import { collectionToPath } from '../../utils/translate'

import { NEW } from '../../utils/config'

const Label = ({ title }) => {
  return <div className="subtitle">{title}</div>
}

class OffererPage extends Component {

  constructor() {
    super()
    this.state = {}
  }

  componentWillUnmount() {
    this.props.resetForm()
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.isNew) return {occasion: {}}
    return {
      offerer: nextProps.offerer
    }
  }

  updateValue = e => {
    this.setState({
      offerer: Object.assign({}, this.state.offerer, {[e.target.name]: e.target.value})
    })
  }

  save = e => {
    e.preventDefault()
    // TODO
  }

  render () {
    const {
      offerer,
      isNew,
    } = this.props
    const {
      address,
      bookingEmail,
      // name,
    } = get(this.state, 'offerer', {})
    const {
      latitude,
      longitude,
      name,
      id,
      siret
    } = get(this.state, 'offerer.venue', {})

    const venueId = isNew ? NEW : id

    return (
      <PageWrapper name='offer' loading={!(offerer || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to={`/${collectionToPath('venues')}`} className="button is-primary is-outlined">Retour</NavLink>
            </div>

            <h1 className='title has-text-centered'>{isNew ? 'Créer' : 'Modifier'} un lieu</h1>
            <form onSubmit={this.save}>
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={siret}
              entityId={venueId}
              label={<Label title="Siret" />}
              name="siret"
              type="siret"
            />
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={name}
              entityId={venueId}
              label={<Label title="Nom" />}
              name="name"
            />
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={address || ''}
              entityId={venueId}
              label={<Label title="Adresse" />}
              name="address"
              type="adress"
            />
            <FormField
              autoComplete="on"
              collectionName="venues"
              defaultValue={bookingEmail || ''}
              entityId={venueId}
              label={<Label title="Email de réservation" />}
              name="bookingEmail"
            />
            <input type='hidden' name='latitude' value={latitude || ''} />
            <input type='hidden' name='longitude' value={longitude || ''} />
            {
              // TODO: plug this to a map
            }

            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                {/* <button className="button is-primary is-medium">Enregistrer</button> */}
                <SubmitButton
                  getBody={form => form.venuesById[venueId]}
                  getIsDisabled={form => !get(form, `venuesById.${venueId}.name`)
                  }
                  className="button is-primary is-medium"
                  method={isNew ? 'POST' : 'PATCH'}
                  path={isNew ? `venues/` : `venues/${venueId}`}
                  storeKey="venues"
                  text="Enregistrer"
                />
              </div>
              <div className="control">
                <NavLink to={`/${collectionToPath('venues')}`} className="button is-primary is-outlined is-medium">Retour</NavLink>
              </div>
            </div>
          </form>
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
      user: get(state, 'data.users.0'),
      // TODO put the following logic in a selector:
      offerer: get(state, 'user.offerers', []).find(o => o.id === get(ownProps, 'match.params.offererId', '')),
      isNew: ownProps.offererId === 'nouveau',
    }),
    { requestData, resetForm }
  )
)(OffererPage)
