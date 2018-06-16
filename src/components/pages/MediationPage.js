import get from 'lodash.get'
import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withCurrentOccasion from '../hocs/withCurrentOccasion'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import UploadThumb from '../layout/UploadThumb'
import { assignData } from '../../reducers/data'
import { showNotification } from '../../reducers/notification'
import selectCurrentMediation from '../../selectors/currentMediation'

const uploadExplanation = `
**Les éléments importants du visuel doivent se situer dans la zone violette : c'est la première vision de l'offre qu'aura l'utilisateur.**

La zone bleue représente le cadrage de l'image dans la fiche détails.
`

class MediationPage extends Component {

  constructor () {
    super()
    this.state = {
      inputUrl: '',
      imageUrl: null,
      image: null,
      croppingRect: null,
    }
  }

  static getDerivedStateFromProps (nextProps, prevState) {
    return {
      inputUrl: prevState.inputUrl,
      imageUrl: prevState.imageUrl || get(nextProps, 'mediation.thumbPath'),
      image: prevState.image,
    }
  }

  static defaultProps = {
    type: 'image',
    imageUploadSize: 400,
    imageUploadBorder: 25,
  }

  handleSuccessData = (state, action) => {
    const {
      method
    } = action
    const {
      history,
      match: { params: { occasionId, occasionPath } },
      showNotification
    } = this.props

    // PATCH
    if (method === 'PATCH' || method === 'POST') {
      history.push('/offres')
      showNotification({
        text: 'Votre accroche a bien été enregistrée',
        type: 'success'
      })
      return
    }
  }

  onImageChange = (image, croppingRect, context) => {
    console.log(croppingRect)
    this.setState({
      image,
      croppingRect,
    })
    this.drawRectangles(context)
  }

  drawRectangles = ctx => {

    if (!ctx) {
      return
    }

    const {
      imageUploadBorder,
      imageUploadSize
    } = this.props

    const size = imageUploadSize + 2 * imageUploadBorder
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

  render () {
    const {
      currentOccasion,
      currentMediation,
      imageUploadSize,
      imageUploadBorder,
      match: {
        params: {
          mediationId,
          occasionId,
          occasionPath
        }
      },
    } = this.props
    const {
      name,
      offererId
    } = (currentOccasion || {})
    const {
      id
    } = (currentMediation || {})
    const {
      croppingRect,
      image,
      imageUrl,
      inputUrl,
    } = this.state
    const isNew = mediationId === 'nouveau'
    const backPath = `/offres/${occasionPath}/${occasionId}`
    return (
      <PageWrapper name='mediation' backTo={{path: backPath, label: 'Revenir à l\'offre'}}>
        <section className='section'>
          <h2 className='subtitle'>{name}</h2>
          <h1 className='pc-title'>
            {isNew ? 'Créez' : 'Modifiez'} une accroche
          </h1>
          <p className='subtitle'>Ajoutez un visuel marquant pour mettre en avant cette offre.</p>
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
              image={imageUrl}
              onImageChange={this.onImageChange}
              borderRadius={0}
              collectionName='mediations'
              entityId={id}
              index={0}
              border={imageUploadBorder}
              width={imageUploadSize}
              height={imageUploadSize}
              storeKey='thumbedMediation'
              type='thumb'
              hasExistingImage={!isNew}
              required
            />
            { imageUrl && (
              <div className='section content'>
                <ReactMarkdown source={uploadExplanation} />
              </div>
            )}
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
            <SubmitButton
              className="button is-primary is-medium"
              getBody={form => {
                if (typeof image === 'string') {
                  return {
                    thumb: image,
                    eventId: occasionId,
                    offererId,
                    croppingRect,
                  }
                }
                const formData = new FormData();
                formData.append('thumb', image)
                formData.append('eventId', occasionId)
                formData.append('offererId', offererId)
                formData.append('croppingRect[x]', croppingRect.x)
                formData.append('croppingRect[y]', croppingRect.y)
                formData.append('croppingRect[width]', croppingRect.width)
                formData.append('croppingRect[height]', croppingRect.height)
                return formData;
              }}
              getIsDisabled={form => !image}
              handleSuccess={this.handleSuccessData}
              method={isNew ? 'POST' : 'PATCH'}
              path={'mediations' + (isNew ? '' : `/${id}`)}
              storeKey="thumb"
              text='Valider'
            />
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
    (state, ownProps) => ({
      currentMediation: selectCurrentMediation(state, ownProps)
    }),
    { assignData, showNotification }
  )
)(MediationPage)
