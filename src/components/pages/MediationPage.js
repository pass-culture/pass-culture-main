import get from 'lodash.get'
import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import UploadThumb from '../layout/UploadThumb'
import { assignData } from '../../reducers/data'
import selectCurrentMediation from '../../selectors/currentMediation'
import selectSelectedOffererId from '../../selectors/selectedOffererId'


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

  // componentDidUpdate (prevProps) {
  //   const {
  //     assignData,
  //     history,
  //     thumbedMediation
  //   } = this.props

  //   const id = get(this.props, 'mediation.id')
  //   if (!get(prevProps, 'mediation.id') && id) {
  //     history.push(`${this.state.routePath}/${id}`)
  //   }

  //   if (thumbedMediation && !prevProps.thumbedMediation) {
  //     history.push(this.state.routePath)
  //   }
  // }

  // componentWillUnmount () {
  //   this.props.assignData({
  //     thumbedMediation: null,
  //     mediations: null
  //   })
  // }

  onImageChange = (image, context) => {
    if (!image) return
    this.drawRectangles(image, context)
    this.setState({
      image
    })
  }

  drawRectangles = (image, ctx) => {
    const size = this.props.imageUploadSize + 2 * this.props.imageUploadBorder
    const firstDimensions = [
      this.props.imageUploadBorder + size / 7.5,
      this.props.imageUploadBorder + size / 32,
      size - 2 * (this.props.imageUploadBorder + size / 7.5),
      size - 2 * (this.props.imageUploadBorder + size / 32),
    ]

    const secondDimensions = [
      this.props.imageUploadBorder + size / 6,
      this.props.imageUploadBorder + size / 4.5,
      size - 2 * (this.props.imageUploadBorder + size / 6),
      size / 2.7 - 2 * (this.props.imageUploadBorder),
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
      occasion,
      offererId,
      imageUploadSize,
      imageUploadBorder,
      selectedOffererId,
      match: {
        params: {
          mediationId,
          occasionId,
          occasionPath
        }
      },
    } = this.props
    const {
      id
    } = (this.props.mediation || {})
    const {
      image,
      imageUrl,
      inputUrl,
    } = this.state

    const isNew = mediationId === 'nouveau'
    const backPath = `/offres/${occasionPath}/${occasionId}`

    return (
      <PageWrapper name='mediation' backTo={{path: backPath, label: 'Revenir à l\'offre'}}>
        <section className='section'>
          <h2 className='subtitle'>{get(occasion, 'name')}</h2>
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
              getBody={form => {
                const formData = new FormData();
                formData.append('thumb', this.state.image)
                formData.append('eventId', occasion.id)
                formData.append('offererId', offererId)
                return formData
              }}
              getIsDisabled={form => !this.state.image}
              className="button is-primary is-medium"
              method={isNew ? 'POST' : 'PATCH'}
              path={'mediations' + (isNew ? '' : `/${id}`)}
              text='Valider'
              storeKey="thumb"
              isMultipart
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
      mediation: selectCurrentMediation(state, ownProps),
      offererId: get(ownProps.occasion, 'occurences.0.venue.managingOffererId'), // TODO: add offererId to occasion object
    }),
    { assignData }
  )
)(MediationPage)
