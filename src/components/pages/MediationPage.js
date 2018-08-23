import classnames from 'classnames'
import get from 'lodash.get'
import { requestData, showNotification } from 'pass-culture-shared'
import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Main from '../layout/Main'
import UploadThumb from '../layout/UploadThumb'
import mediationSelector from '../../selectors/mediation'
import offerSelector from '../../selectors/offer'
import offererSelector from '../../selectors/offerer'
import venueSelector from '../../selectors/venue'
import { mediationNormalizer, offerNormalizer } from '../../utils/normalizers'

const uploadExplanation = `
**Les éléments importants du visuel doivent se situer dans la zone violette : c'est la première vision de l'offre qu'aura l'utilisateur.**

La zone bleue représente le cadrage de l'image dans la fiche détails.
`

class MediationPage extends Component {
  constructor() {
    super()
    this.state = {
      croppingRect: null,
      inputUrl: '',
      imageUrl: null,
      image: null,
      isLoading: false,
    }
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const {
      match: {
        params: { mediationId },
      },
    } = nextProps
    return {
      imageUrl: prevState.imageUrl || get(nextProps, 'mediation.thumbPath'),
      isNew: mediationId === 'nouveau',
    }
  }

  static defaultProps = {
    type: 'image',
    imageUploadSize: 400,
    imageUploadBorder: 25,
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match: {
        params: { mediationId, offerId },
      },
      offer,
      requestData,
    } = this.props
    const { isNew } = this.state
    !offer &&
      requestData('GET', `offers/${offerId}`, {
        key: 'offers',
        normalizer: offerNormalizer,
      })
    if (!isNew) {
      requestData('GET', `mediations/${mediationId}`, {
        handleSuccess,
        handleFail,
        key: 'mediations',
        normalizer: mediationNormalizer,
      })
      return
    }
    handleSuccess()
  }

  handleSuccessData = (state, action) => {
    const { history, showNotification, offer } = this.props

    this.setState({ isLoading: false }, () => {
      history.push(`/offres/${offer.id}`)
      showNotification({
        text: 'Votre accroche a bien été enregistrée',
        type: 'success',
      })
    })
  }

  onImageChange = (context, image, croppingRect) => {
    this.setState({
      image,
      croppingRect,
    })
    this.drawRectangles(context)
  }

  drawRectangles = ctx => {
    const { imageUploadBorder, imageUploadSize } = this.props

    const size =
      window.devicePixelRatio * (imageUploadSize + 2 * imageUploadBorder)
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
    ctx.beginPath()
    ctx.lineWidth = '2'
    ctx.strokeStyle = '#b921d7'
    ctx.rect(...firstDimensions)
    ctx.stroke()

    // Second rectangle
    ctx.beginPath()
    ctx.strokeStyle = '#54c7fc'
    ctx.rect(...secondDimensions)
    ctx.stroke()
  }

  onOkClick = e => {
    this.state.inputUrl &&
      this.setState({
        imageUrl: this.state.inputUrl,
      })
  }

  onSubmit = () => {
    const { match, mediation, offerer, requestData } = this.props
    const { croppingRect, image, credit, isNew } = this.state

    const offererId = get(offerer, 'id')
    const offerId = match.params.offerId

    let body
    if (typeof image === 'string') {
      body = {
        croppingRect,
        offererId,
        offerId,
        credit,
        thumb: image,
      }
    } else {
      const formData = new FormData()
      formData.append('offererId', offererId)
      formData.append('offerId', offerId)
      formData.append('credit', credit)
      formData.append('thumb', image)
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
        key: 'mediations',
      }
    )
  }

  render() {
    const {
      imageUploadSize,
      imageUploadBorder,
      match: {
        params: { offerId },
      },
      mediation,
      offer,
    } = this.props
    const { name } = offer || {}
    const { image, credit, imageUrl, inputUrl, isLoading, isNew } = this.state
    const backPath = `/offres/${offerId}`

    return (
      <Main
        name="mediation"
        backTo={{ path: backPath, label: "Revenir à l'offre" }}
        handleDataRequest={this.handleDataRequest}>
        <section className="section hero">
          <h2 className="subtitle has-text-weight-bold">{name}</h2>
          <h1 className="main-title">
            {isNew ? 'Créez' : 'Modifiez'} une accroche
          </h1>
          <p className="subtitle">
            Ajoutez un visuel marquant pour mettre en avant cette offre.
            <br />
            <span className="label">Le fichier doit peser 100Ko minimum.</span>
          </p>
        </section>

        <div className="section">
          <label className="label">Depuis une adresse Internet :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                type="url"
                className="input is-rounded"
                placeholder="URL du fichier"
                value={inputUrl}
                onChange={e => this.setState({ inputUrl: e.target.value })}
              />
            </p>
            <p className="control">
              <button
                className="button is-primary is-outlined is-medium"
                onClick={this.onOkClick}>
                OK
              </button>
            </p>
          </div>
        </div>
        <div className="section columns">
          <div className="column is-three-quarters">
            <label className="label">... ou depuis votre poste :</label>
            <UploadThumb
              border={imageUploadBorder}
              borderRadius={0}
              collectionName="mediations"
              entityId={get(mediation, 'id')}
              hasExistingImage={!isNew}
              height={imageUploadSize}
              image={imageUrl}
              index={0}
              width={imageUploadSize}
              required
              onImageChange={this.onImageChange}
              storeKey="mediations"
              type="thumb"
            />
            {image && (
              <div className="section content">
                <ReactMarkdown source={uploadExplanation} />
              </div>
            )}
          </div>
          <div className="column is-one-quarter">
            <div className="section">
              <h6>Exemple :</h6>
              <img
                src="/mediation-example.png"
                title="Exemple de cadrage"
                alt="Explication"
              />
            </div>
          </div>
        </div>
        <div className="section">
          <div className="field-group">
            <div className="field">
              <label className="label">Crédit photo</label>
              <input
                id="mediation-credit"
                type="text"
                className="input is-rounded"
                value={credit}
                onChange={e => this.setState({ credit: e.target.value })}
              />
            </div>
          </div>
        </div>
        <hr />
        <div
          className="field is-grouped is-grouped-centered"
          style={{ justifyContent: 'space-between' }}>
          <div className="control">
            <NavLink
              to={backPath}
              className="button is-primary is-outlined is-medium">
              Annuler
            </NavLink>
          </div>
          <div className="control">
            <button
              className={classnames('button is-primary is-medium', {
                'is-loading': isLoading,
              })}
              disabled={!image}
              onClick={this.onSubmit}>
              Valider
            </button>
          </div>
        </div>
      </Main>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const offer = offerSelector(state, ownProps.match.params.offerId)
      const venue = venueSelector(state, get(offer, 'venueId'))
      return {
        offer,
        offerer: offererSelector(state, get(venue, 'managingOffererId')),
        mediation: mediationSelector(state, ownProps.match.params.mediationId),
      }
    },
    { requestData, showNotification }
  )
)(MediationPage)
