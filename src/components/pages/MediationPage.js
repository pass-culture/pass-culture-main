import classnames from 'classnames'
import get from 'lodash.get'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import PageWrapper from '../layout/PageWrapper'
import UploadThumb from '../layout/UploadThumb'
import { showNotification } from '../../reducers/notification'
import mediationSelector from '../../selectors/mediation'
import occasionSelector from '../../selectors/occasion'
import offererSelector from '../../selectors/offerer'
import venueSelector from '../../selectors/venue'
import { mediationNormalizer, occasionNormalizer } from '../../utils/normalizers'


const uploadExplanation = `
**Les éléments importants du visuel doivent se situer dans la zone violette : c'est la première vision de l'offre qu'aura l'utilisateur.**

La zone bleue représente le cadrage de l'image dans la fiche détails.
`

class MediationPage extends Component {

  constructor () {
    super()
    this.state = {
      croppingRect: null,
      inputUrl: '',
      imageUrl: null,
      image: null,
      isLoading: false,
    }
  }

  static getDerivedStateFromProps (nextProps, prevState) {
    const {
      match: { params: { mediationId } }
    } = nextProps
    return {
      inputUrl: prevState.inputUrl,
      imageUrl: prevState.imageUrl || get(nextProps, 'mediation.thumbPath'),
      image: prevState.image,
      isNew: mediationId === 'nouveau'
    }
  }

  static defaultProps = {
    type: 'image',
    imageUploadSize: 400,
    imageUploadBorder: 25,
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match: { params: { mediationId, occasionId } },
      occasion,
      requestData
    } = this.props
    const { isNew } = this.state
    !occasion && requestData(
      'GET',
      `occasions/${occasionId}`,
      {
        key: 'occasions',
        normalizer: occasionNormalizer
      }
    )
    if (!isNew) {
     requestData(
        'GET',
        `mediations/${mediationId}`,
        {
          handleSuccess,
          handleFail,
          key: 'mediations',
          normalizer: mediationNormalizer
        }
      )
      return
    }
    handleSuccess()
  }

  handleSuccessData = (state, action) => {
    const {
      method
    } = action
    const {
      history,
      showNotification,
      occasion,
    } = this.props

    this.setState(
      { isLoading: false },
      () => {
        history.push(`/offres/${occasion.id}`)

        // TODO
        showNotification({
          text: 'Votre accroche a bien été enregistrée',
          type: 'success'
        })
      }
    )

  }

  onImageChange = (context, image, croppingRect) => {
    this.setState({
      image,
      croppingRect,
    })
    this.drawRectangles(context)
  }

  drawRectangles = ctx => {

    const {
      imageUploadBorder,
      imageUploadSize
    } = this.props

    const size = window.devicePixelRatio * (imageUploadSize + 2 * imageUploadBorder)
    const firstDimensions = [
      imageUploadBorder + size / 7.5,
      imageUploadBorder + size / 32,
      size - 2 * (imageUploadBorder + size / 7.5),
      size - 2 * (imageUploadBorder + size / 32),
    ]

    const secondDimensions = [
      imageUploadBorder + size / 6,
      imageUploadBorder + size / 4.5,
      size - 2 * (imageUploadBorder + size / 6),
      size / 2.7 - 2 * imageUploadBorder,
    ]

    // First rectangle
    ctx.beginPath();
    ctx.lineWidth='2';
    ctx.strokeStyle='#b921d7';
    ctx.rect(...firstDimensions);
    ctx.stroke();

    // Second rectangle
    ctx.beginPath();
    ctx.strokeStyle='#54c7fc';
    ctx.rect(...secondDimensions);
    ctx.stroke();
  }

  onOkClick = e => {
    console.log(this.state.inputUrl)
    this.state.inputUrl && this.setState({
      imageUrl: this.state.inputUrl
    })
  }

  onSubmit = () => {
    const {
      mediation,
      occasion,
      occasionId,
      offerer,
      requestData
    } = this.props
    const {
      croppingRect,
      image,
      isNew
    } = this.state

    const eventId = get(occasion, 'eventId')
    const offererId = get(offerer, 'id')
    const thingId = get(occasion, 'thingId')

    let body
    if (typeof image === 'string') {
      body = {
        croppingRect,
        eventId: occasionId,
        offererId,
        thingId,
        thumb: image,
      }
    } else {
      const formData = new FormData();
      formData.append('thumb', image)
      formData.append('eventId', eventId)
      formData.append('thingId', thingId)
      formData.append('offererId', offererId)
      formData.append('croppingRect[x]', croppingRect.x)
      formData.append('croppingRect[y]', croppingRect.y)
      formData.append('croppingRect[width]', croppingRect.width)
      formData.append('croppingRect[height]', croppingRect.height)
      body = formData
    }

    this.setState({ isLoading: true })

    requestData(
      isNew ? 'POST' : 'PATCH',
      `mediations${isNew ? '' : `/${get(mediation, 'id')}`}`,
      {
        body,
        encode: 'multipart/form-data',
        handleSuccess: this.handleSuccessData,
        key: 'mediations'
      }
    )
  }

  render () {
    const {
      imageUploadSize,
      imageUploadBorder,
      match: {
        params: {
          occasionId
        }
      },
      mediation,
      occasion,
    } = this.props
    const {
      name
    } = (occasion || {})
    const {
      image,
      imageUrl,
      inputUrl,
      isLoading,
      isNew
    } = this.state
    const backPath = `/offres/${occasionId}`

    return (
      <PageWrapper
        name='mediation'
        backTo={{path: backPath, label: 'Revenir à l\'offre'}}
        handleDataRequest={this.handleDataRequest} >
        <section className='section hero'>
          <h2 className='subtitle has-text-weight-bold'>
            {name}
          </h2>
          <h1 className='main-title'>
            {isNew ? 'Créez' : 'Modifiez'} une accroche
          </h1>
          <p className='subtitle'>
            Ajoutez un visuel marquant pour mettre en avant cette offre.
            <br />
            <span className="label">
              Le fichier doit peser 100Ko minimum.
            </span>
          </p>
        </section>

        <div className='section'>
          <label className="label">Depuis une adresse Internet :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                type='url'
                className='input is-rounded'
                placeholder='URL du fichier'
                value={inputUrl}
                onChange={e => this.setState({inputUrl: e.target.value})}
              />
            </p>
            <p className="control">
              <button className='button is-primary is-outlined is-medium' onClick={this.onOkClick}>OK</button>
            </p>
          </div>
        </div>
        <div className='section columns'>
          <div className='column is-three-quarters'>
            <label className='label'>... ou depuis votre poste :</label>
            <UploadThumb
              border={imageUploadBorder}
              borderRadius={0}
              collectionName='mediations'
              entityId={get(mediation, 'id')}
              hasExistingImage={!isNew}
              height={imageUploadSize}
              image={imageUrl}
              index={0}
              width={imageUploadSize}
              required
              onImageChange={this.onImageChange}
              storeKey='mediations'
              type='thumb' />
            {
              image && (
                <div className='section content'>
                  <ReactMarkdown source={uploadExplanation} />
                </div>
              )
            }
          </div>
          <div className='column is-one-quarter'>
            <div className='section'>
              <h6>Exemple :</h6>
              <img src='/mediation-example.png' title='Exemple de cadrage' alt='Explication' />
            </div>
          </div>
        </div>
        <hr />
        <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
          <div className="control">
            <NavLink to={backPath}
              className="button is-primary is-outlined is-medium">
              Annuler
            </NavLink>
          </div>
          <div className="control">
            <button
              className={classnames("button is-primary is-medium", {
                'is-loading': isLoading
              })}
              disabled={!image}
              onClick={this.onSubmit}>
              Valider
            </button>
          </div>
        </div>
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const venue = venueSelector(state, get(occasion, 'venueId'))
      return {
        occasion,
        offerer: offererSelector(state, get(venue, 'managingOffererId')),
        mediation: mediationSelector(state, ownProps.match.params.mediationId),
      }
    },
    { requestData, showNotification }
  )
)(MediationPage)
