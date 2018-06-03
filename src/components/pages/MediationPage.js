import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'
import { resetForm } from '../../reducers/form'
import selectCurrentOccasion from '../../selectors/currentOccasion'
import selectCurrentMediation from '../../selectors/currentMediation'


class MediationPage extends Component {

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

  onSubmitClick = () => {
    this.props.resetForm()
  }

  render () {
    const {
      mediationId,
      occasionId,
      occasionPath
    } = this.props.match.params
    const {
      id,
      occasion,
    } = this.props
    const isNew = mediationId === 'nouveau'
    return (
      <PageWrapper name='mediation' loading={!(id || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink
                to={`/offres/${occasionPath}/${occasionId}`}
                className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>
            <br/>
            <section className='section'>
              <h2 className='subtitle'>
                {get(occasion, 'name')}
              </h2>
              <br/>
              <h1 className='title has-text-centered'>
                {isNew ? 'Créez' : 'Modifiez'} une accroche
              </h1>
              <p>Ajoutez un visuel marquant pour mettre en avant cette offre.</p>
            </section>
            <FormField
              collectionName='mediations'
              entityId={id}
              type='thumb'
              required />
            {/*
            <form>
              <div className='field'>
                <label className="label">
                  <Label title='Depuis une adresse Internet :' />
                </label>
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
                <label className="label">
                  <Label title='... ou depuis votre poste :' />
                </label>
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
            */}
          </div>
        </div>
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) =>
      Object.assign({
        user: state.user,
        occasion: selectCurrentOccasion(state, ownProps),
      }, selectCurrentMediation(state, ownProps)),
    { resetForm, requestData }
  )
)(MediationPage)
