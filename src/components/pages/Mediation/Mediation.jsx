import classnames from 'classnames'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'

import Titles from '../../layout/Titles/Titles'
import Main from '../../layout/Main'
import UploadThumbContainer from '../../layout/UploadThumb/UploadThumbContainer'
import CanvasTools from '../../../utils/canvas'

const IMAGE_UPLOAD_SIZE = 400
const IMAGE_UPLOAD_BORDER = 25

class Mediation extends PureComponent {
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

  handleOnChange = event => this.setState({ credit: event.target.value })

  onHandleDataRequest = (handleSuccess, handleFail) => {
    const {
      getMediation,
      getOffer,
      match: {
        params: { mediationId, offerId },
      },
      offer,
    } = this.props
    const { isNew } = this.state
    if (!offer) {
      getOffer(offerId)
    }
    if (!isNew) {
      getMediation(mediationId, handleSuccess, handleFail)
      return
    }
    handleSuccess()
  }

  handleFailData = (state, action) => {
    const { history, offer, showOfferModificationErrorNotification } = this.props
    const {
      payload: { errors },
    } = action

    this.setState({ isLoading: false }, () => {
      history.push(`/offres/${offer.id}`)
      let error
      if (errors && errors.thumb && errors.thumb[0]) {
        error = errors.thumb[0]
      } else if (errors && errors.thumbUrl && errors.thumbUrl[0]) {
        error = errors.thumbUrl[0]
      }
      showOfferModificationErrorNotification(error)
    })
  }

  handleSuccessData = () => {
    const { history, offer, showOfferModificationValidationNotification } = this.props

    this.setState({ isLoading: false }, () => {
      history.push(`/offres/${offer.id}`)
      showOfferModificationValidationNotification()
    })
  }

  handleOnImageChange = (context, image, croppingRect) => {
    this.setState({
      image,
      croppingRect,
    })
    this.drawRectangles(context)
  }

  drawRectangles = ctx => {
    const cvs = new CanvasTools(ctx)

    const purpleRectangle = {
      width: 2,
      color: '#b921d7',
      coordinates: [IMAGE_UPLOAD_BORDER, IMAGE_UPLOAD_BORDER, IMAGE_UPLOAD_SIZE, IMAGE_UPLOAD_SIZE],
    }

    cvs.drawArea(purpleRectangle)
    cvs.drawLabel({
      fontFamily: 'barlow',
      fontSize: 14,
      fontWeight: 'bold',
      parent: purpleRectangle,
      text: '1',
      color: 'white',
      width: 20,
    })

    const greenVerticalMargin = 57
    const greenHorizontalMargin = 11
    const greenRectangle = {
      width: 2,
      color: '#4CD964',
      coordinates: [
        IMAGE_UPLOAD_BORDER + greenVerticalMargin,
        IMAGE_UPLOAD_BORDER + greenHorizontalMargin,
        // Margins have to be removed 2 times,
        // one for each sides of the rectangle
        IMAGE_UPLOAD_SIZE - greenVerticalMargin * 2,
        IMAGE_UPLOAD_SIZE - greenHorizontalMargin * 2,
      ],
    }
    cvs.drawArea(greenRectangle)
    cvs.drawLabel({
      parent: greenRectangle,
      text: '2',
      color: 'white',
      width: 20,
    })

    const dashedVerticalMargin = 72
    const dashedHorizontalMargin = 80
    const dashedHeight = 160
    const dashedRectangle = [
      0.5 + IMAGE_UPLOAD_BORDER + dashedVerticalMargin,
      0.5 + IMAGE_UPLOAD_BORDER + dashedHorizontalMargin,
      0.5 + IMAGE_UPLOAD_SIZE - dashedVerticalMargin * 2,
      0.5 + dashedHeight,
    ]

    const dash = {
      length: 10,
      space: 4,
    }

    cvs.drawDashed({
      coordinates: dashedRectangle,
      dash,
      color: 'white',
    })

    cvs.drawDashed({
      coordinates: cvs.shift(dashedRectangle),
      dash,
      color: 'black',
    })
  }

  handleOnOkClick = () => {
    const { inputUrl } = this.state

    inputUrl &&
      this.setState({
        image: null,
        imageUrl: inputUrl,
      })
  }

  handleOnSubmit = () => {
    const { match, mediation, offerer, createOrUpdateMediation } = this.props
    const { croppingRect, image, credit, isNew } = this.state

    const offererId = get(offerer, 'id')
    const offerId = match.params.offerId

    const body = new FormData()
    body.append('offererId', offererId)
    body.append('offerId', offerId)
    body.append('credit', credit)
    if (typeof image === 'string') {
      body.append('thumbUrl', image)
    } else {
      body.append('thumb', image)
    }
    body.append('croppingRect[x]', croppingRect.x)
    body.append('croppingRect[y]', croppingRect.y)
    body.append('croppingRect[width]', croppingRect.width)
    body.append('croppingRect[height]', croppingRect.height)

    this.setState({ isLoading: true })
    createOrUpdateMediation(isNew, mediation, body, this.handleFailData, this.handleSuccessData)
  }

  handleOnUrlChange = event => {
    this.setState({ inputUrl: event.target.value })
  }

  handleOnUploadClick = event => {
    this.setState({
      image: event.target.files[0],
      imageUrl: null,
      inputUrl: '',
    })
  }

  render() {
    const {
      match: {
        params: { offerId },
      },
      mediation,
    } = this.props
    const { image, credit, imageUrl, inputUrl, isLoading, isNew } = this.state
    const backPath = `/offres/${offerId}`

    const fragment = (
      <Fragment>
        <div className="thumbnailManager">
          <div className="section ">
            <h2 className="has-text-primary has-text-weight-semibold active">
              {'Comment cadrer votre image d’accroche'}
            </h2>
            <ul>
              <li className="mb12">
                <span className="li-number">
                  {'1'}
                </span>
                <span>
                  {'Le visuel doit '}
                  <b>
                    {'remplir le cadre 1 violet'}
                  </b>
                  {'.'}
                </span>
              </li>
              <li className="mb12">
                <span className="li-number">
                  {'2'}
                </span>
                <span>
                  <b>
                    {'Les éléments importants '}
                  </b>
                  {' (p. ex. un visage, une zone d’intérêt…) doivent se situer '}
                  <b>
                    {'dans le cadre 2 vert.'}
                  </b>
                  <br />
                  {' C’est la première vision de l’offre qu’aura l’utilisateur.'}
                </span>
              </li>
            </ul>
            {
              'La zone en pointillés représente la partie visible de l’image dans la fiche détail de l’offre.'
            }
          </div>
          <div className="section">
            <div className="row">
              <div className="section">
                <h6>
                  {'Exemples :'}
                </h6>
                <div className="columns crop-explain">
                  <div className="column">
                    <img
                      alt="Explication"
                      src="/bad-crop.png"
                      title="Exemple de cadrage"
                    />
                  </div>
                  <div className="column explain-text explain-bad">
                    <p>
                      <b>
                        {'Mauvais cadrage'}
                      </b>
                      {'Les éléments importants sont hors-cadre.'}
                    </p>
                  </div>
                  <div className="column">
                    <img
                      alt="Explication"
                      src="/good-crop.png"
                      title="Exemple de cadrage"
                    />
                  </div>
                  <div className="column explain-text explain-good">
                    <p>
                      <b>
                        {'Cadrage idéal'}
                      </b>
                      {'Les éléments importants sont visibles dans tous les cadres.'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <hr className="dotted" />
            <div className="row">
              <UploadThumbContainer
                border={IMAGE_UPLOAD_BORDER}
                borderRadius={0}
                collectionName="mediations"
                entityId={get(mediation, 'id')}
                hasExistingImage={!isNew}
                height={IMAGE_UPLOAD_SIZE}
                image={image || imageUrl}
                index={0}
                onImageChange={this.handleOnImageChange}
                readOnly
                required
                storeKey="mediations"
                type="thumb"
                width={IMAGE_UPLOAD_SIZE}
              />
            </div>
          </div>
        </div>
        <div className="section">
          <div className="field-group">
            <div className="field">
              <label className="label">
                {'Crédit photo'}
              </label>
              <input
                className="input is-rounded"
                id="mediation-credit"
                onChange={this.handleOnChange}
                type="text"
                value={credit}
              />
            </div>
          </div>
        </div>
        <hr />
        <div
          className="field is-grouped is-grouped-centered"
          style={{ justifyContent: 'space-between' }}
        >
          <div className="control">
            <NavLink
              className="button is-primary is-outlined is-medium"
              to={backPath}
            >
              {'Annuler'}
            </NavLink>
          </div>
          <div className="control">
            <button
              className={classnames('button is-primary is-medium', {
                'is-loading': isLoading,
              })}
              disabled={!image}
              onClick={this.handleOnSubmit}
              type="button"
            >
              {'Valider '}
            </button>
          </div>
        </div>
      </Fragment>
    )

    const $imageSections = (image || imageUrl) && fragment

    return (
      <Main
        backTo={{ path: backPath, label: 'Revenir à l’offre' }}
        handleDataRequest={this.onHandleDataRequest}
        name="mediation"
      >
        <Titles title={`${isNew ? 'Créez' : 'Modifiez'} une accroche`} />
        <p className="advice">
          {'Ajoutez un visuel marquant pour mettre en avant cette offre.'}
        </p>
        <p>
          <b>
            {'L’accroche permet d’afficher votre offre "à la une" de l’app, '}
          </b>
          {
            'et la rend visuellement plus attrayante. C’est une image (et bientôt une phrase ou une vidéo) intrigante, percutante, séduisante...'
          }
          <br />
          {'en un mot : accrocheuse.'}
        </p>
        <p>
          {
            'Les accroches font la spécificité du pass Culture. Prenez le temps de les choisir avec soin ! '
          }
        </p>
        <p>
          {'Utilisateurs avancés : vous pouvez '}
          <a href="https://pass.culture.fr/assets/docs/PassCulture-accroche-template-20181114.zip">
            {'télécharger ici les gabarits Illustrator et Photoshop.'}
          </a>
        </p>

        <div className="section">
          <label className="label">
            {'Depuis une adresse Internet :'}
          </label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                className="input is-rounded"
                onChange={this.handleOnUrlChange}
                placeholder="URL du fichier"
                type="url"
                value={inputUrl}
              />
            </p>
            <p className="control">
              <button
                className="button is-primary is-outlined is-medium"
                onClick={this.handleOnOkClick}
                type="button"
              >
                {'OK'}
              </button>
            </p>
          </div>
        </div>

        <div className="section">
          <label className="label">
            {'...ou depuis votre poste : '}
          </label>
          <label className="button is-primary is-outlined">
            {'Choisir un fichier '}
            <input
              hidden
              onChange={this.handleOnUploadClick}
              type="file"
            />
          </label>
        </div>
        {$imageSections}
      </Main>
    )
  }
}

Mediation.defaultProps = {
  mediation: {},
}

Mediation.propTypes = {
  createOrUpdateMediation: PropTypes.func.isRequired,
  getMediation: PropTypes.func.isRequired,
  getOffer: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  mediation: PropTypes.shape(),
  offer: PropTypes.shape().isRequired,
  offerer: PropTypes.shape().isRequired,
  showOfferModificationErrorNotification: PropTypes.func.isRequired,
  showOfferModificationValidationNotification: PropTypes.func.isRequired,
}

export default Mediation
