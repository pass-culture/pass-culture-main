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
import selectCurrentMediation from '../../selectors/currentMediation'
import selectOccasionPath from '../../selectors/occasionPath'
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
      isNew,
      mediation,
      occasion,
      occasionId,
      occasionPath,
    } = this.props

    const {
      id
    } = mediation

    const mediationId = isNew ? NEW : this.props.mediationId
    return (
      <PageWrapper name='mediation' loading={!(id || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to={`/offres/${occasionPath}/${occasionId}`} className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>
            <section className='section'>
              <h2 className='subtitle'>{get(occasion, 'name')}</h2>
              <h1 className='title has-text-centered'>
                {isNew ? 'Créez' : 'Modifiez'} une accroche
              </h1>
              <p>Ajoutez un visuel marquant pour mettre en avant cette offre.</p>
              </section>
            <form>
              <div className='field'>
                <label class="label"><Label title='Depuis une adresse Internet :' /></label>
                <div className="field is-grouped">
                  <p className="control is-expanded">
                    <input className="input is-rounded" type="url" placeholder="http://www.example.com" />
                  </p>
                  <p className="control">
                    <a className="button is-primary is-outlined is-medium">
                      OK
                    </a>
                  </p>
                </div>
              </div>
              <div className='field'>
                <label class="label"><Label title='... ou depuis votre poste :' /></label>
                <div className="file is-primary is-outlined">
                  <label className="file-label">
                    <input className="file-input" type="file" name="resume" />
                    <span className="file-cta">
                      <span className="file-label">
                        Choisir un fichier
                      </span>
                    </span>
                  </label>
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
    (state, ownProps) => {
      return Object.assign({
        isNew: ownProps.match.params.mediationId === 'nouveau',
        user: state.user,
        mediation: selectCurrentMediation(state, ownProps),
        occasionPath: ownProps.match.params.occasionPath,
        occasionId: ownProps.match.params.occasionId,
        occasion: selectCurrentOccasion(state, ownProps),
      })
    },
    { resetForm, requestData }
  )
)(MediationPage)
