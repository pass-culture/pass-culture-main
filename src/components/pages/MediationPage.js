import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'

import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { requestData } from '../../reducers/data'
import { resetForm } from '../../reducers/form'
import selectCurrentOccasion from '../../selectors/currentOccasion'
import selectCurrentPath from '../../selectors/currentPath'
import selectEventTypes from '../../selectors/eventTypes'
import { NEW } from '../../utils/config'

const Label = ({ title }) => {
  return <div className="subtitle">{title}</div>
}

class MediationPage extends Component {

  constructor() {
    super()
    this.state = {
      mediation: null,
    }
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.isNew) return {mediation: {}}
    return {
      mediation: nextProps.mediation
    }
  }

  handleRequestData = () => {
    // TODO: replug
    // const {
    //   collectionName,
    //   occasionId,
    //   requestData,
    // } = this.props
    // occasionId !== 'nouveau' && requestData(
    //   'GET',
    //   `occasions/${collectionName}/${occasionId}`,
    //   { key: 'occasions' }
    // )
  }

  componentDidMount() {
    this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { mediation, mediationId } = this.props
    if (!mediation && mediationId !== prevProps.mediationId) {
      this.handleRequestData()
    }
  }

  // updateOccasion = (key, value) => {
  //   const newValue = key.split('.').reverse().reduce((result, keyElement) => {
  //     return {[keyElement]: (result || value)}
  //   }, null)
  //   this.setState({
  //     occasion: Object.assign({}, this.state.occasion, newValue)
  //   })
  // }

  onSubmitClick = () => {
    this.props.resetForm()
  }

  render () {
    const {
      author,
      bookingLimitDatetime,
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      eventTypes,
      id,
      isNew,
      mediaUrls,
      name,
      occasion,
      occasionId,
      occasionType,
      occurences,
      path,
      performer,
      stageDirector,
      type
    } = this.props
    const mediationId = isNew ? NEW : this.props.mediationId
    console.log(occasion)
    return (
      <PageWrapper name='mediation' loading={!(id || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to={`/offres/${occasionType}/${occasionId}`} className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>
            <h2 className='subtitle'>{get(occasion, 'name')}</h2>
            <h1 className='title has-text-centered'>
              {isNew ? 'Créez' : 'Modifiez'} une accroche
            </h1>
            <form>
              <p>Ajoutez un visuel marquant pour mettre en avant cette offre.</p>
              <FormField
                autoComplete="url"
                collectionName="events"
                entityId={id}
                label={<Label title="Depuis une adresse Internet :" />}
                name="url"
                type='url'
              />
              <div className="file">
                <label className="file-label">
                  <input className="file-input" type="file" name="resume" />
                  <span className="file-cta">
                    <span className="file-icon">
                      <i className="fas fa-upload"></i>
                    </span>
                    <span className="file-label">
                      Choose a file…
                    </span>
                  </span>
                </label>
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
    (state, ownProps) => {
      return Object.assign({
        collectionName: ownProps.occasionType === 'evenements'
          ? 'events'
          : ownProps.occasionType === 'things'
            ? 'things'
            : null,
        eventTypes: selectEventTypes(state),
        isNew: ownProps.mediationId === 'nouveau',
        path: selectCurrentPath(state, ownProps),
        user: state.user,
        occasion: selectCurrentOccasion(state, ownProps),
      })
    },
    { resetForm, requestData }
  )
)(MediationPage)
