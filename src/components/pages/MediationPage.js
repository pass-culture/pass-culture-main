import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import UploadThumb from '../layout/UploadThumb'
import { assignData } from '../../reducers/data'
import selectCurrentMediation from '../../selectors/currentMediation'
import selectCurrentOfferer from '../../selectors/currentOfferer'
import { pathToModel } from '../../utils/translate'


class MediationPage extends Component {

  constructor () {
    super ()
    this.state = {
      isLoading: false,
      isNew: false
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      mediationId,
      occasionId,
      occasionPath
    } = nextProps.match.params
    const {
      offerer,
      name,
    } = nextProps
    const {
      id
    } = (nextProps.mediation || {})
    const isNew = mediationId === 'nouveau'
    return {
      apiPath: `mediations${isNew ? '' : `/${id}`}`,
      method: isNew ? 'POST' : 'PATCH',
      occasionModel: pathToModel(occasionPath).toLowerCase(),
      isLoading: !(name || offerer || (id && !isNew) ),
      isNew,
      routePath: `/offres/${occasionPath}/${occasionId}/accroches`
    }
  }

  componentDidUpdate (prevProps) {
    const {
      assignData,
      history,
      thumbedMediation
    } = this.props

    const id = get(this.props, 'mediation.id')
    if (!get(prevProps, 'mediation.id') && id) {
      history.push(`${this.state.routePath}/${id}`)
    }

    if (thumbedMediation && !prevProps.thumbedMediation) {
      history.push(this.state.routePath)
    }
  }

  componentWillUnmount () {
    this.props.assignData({
      thumbedMediation: null,
      mediations: null
    })
  }

  render () {
    const {
      offerer,
      name,
    } = this.props
    const occasionId = this.props.id
    const {
      id
    } = (this.props.mediation || {})
    const {
      apiPath,
      isLoading,
      isNew,
      method,
      occasionModel,
      routePath
    } = this.state
    return (
      <PageWrapper name='mediation' loading={isLoading}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink
                to={routePath}
                className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>
            <br/>
            <section className='section' key={0}>
              <h1 className='title has-text-centered'>
                {isNew ? 'Créez' : 'Modifiez'} une accroche pour {name}
              </h1>
            </section>
            <SubmitButton
              getBody={form => ({
                [`${occasionModel}Id`]: occasionId,
                offererId: offerer && offerer.id
              })}
              className="button is-primary is-medium"
              getIsDisabled={form => !offerer || !occasionId}
              method={method}
              path={apiPath}
              storeKey="mediations"
              text={isNew ? 'Créer' : 'Modifier'}
            />
            <br/>
            <br/>
            {
              !isNew && [
                <section className='section' key={0}>
                  <p>Ajoutez un visuel marquant pour mettre en avant cette offre.</p>
                </section>,
                <UploadThumb
                  borderRadius={0}
                  collectionName='mediations'
                  entityId={id}
                  key={1}
                  index={0}
                  storeKey='thumbedMediation'
                  type='thumb'
                  required
                />
              ]
            }
          </div>
        </div>
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion,
  connect(
    (state,ownProps) => ({
      thumbedMediation: state.data.thumbedMediation,
      mediation: selectCurrentMediation(state, ownProps),
      offerer: selectCurrentOfferer(state, ownProps)
    }),
    { assignData }
  )
)(MediationPage)
