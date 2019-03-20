import classnames from 'classnames'
import get from 'lodash.get'
import { showNotification } from 'pass-culture-shared'
import React, { PureComponent, Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'
import HeroSection from 'components/layout/HeroSection'
import Main from 'components/layout/Main'
import UploadThumb from 'components/layout/UploadThumb'
import selectMediationById from 'selectors/selectMediationById'
import selectOfferById from 'selectors/selectOfferById'
import selectOffererById from 'selectors/selectOffererById'
import selectVenueById from 'selectors/selectVenueById'
import { mediationNormalizer, offerNormalizer } from 'utils/normalizers'
import CanvasTools from 'utils/canvas'

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

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      dispatch,
      match: {
        params: { mediationId, offerId },
      },
      offer,
    } = this.props
    const { isNew } = this.state
    !offer &&
      dispatch(
        requestData({
          apiPath: `/offers/${offerId}`,
          normalizer: offerNormalizer,
        })
      )
    if (!isNew) {
      dispatch(
        requestData({
          apiPath: `/mediations/${mediationId}`,
          handleSuccess,
          handleFail,
          normalizer: mediationNormalizer,
        })
      )
      return
    }
    handleSuccess()
  }

  handleFailData = (state, action) => {
    const { dispatch, history, offer } = this.props
    const {
      payload: { errors },
    } = action

    this.setState({ isLoading: false }, () => {
      history.push(`/offres/${offer.id}`)
      dispatch(
        showNotification({
          text: errors.thumb[0],
          type: 'fail',
        })
      )
    })
  }

  handleSuccessData = () => {
    const { dispatch, history, offer } = this.props

    this.setState({ isLoading: false }, () => {
      history.push(`/offres/${offer.id}`)
      dispatch(
        showNotification({
          text: 'Votre accroche a bien été enregistrée',
          type: 'success',
        })
      )
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
    const cvs = new CanvasTools(ctx)

    const purpleRectangle = {
      width: 2,
      color: '#b921d7',
      coordinates: [
        IMAGE_UPLOAD_BORDER,
        IMAGE_UPLOAD_BORDER,
        IMAGE_UPLOAD_SIZE,
        IMAGE_UPLOAD_SIZE,
      ],
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

  onOkClick = e => {
    this.state.inputUrl &&
      this.setState({
        image: null,
        imageUrl: this.state.inputUrl,
      })
  }

  onSubmit = () => {
    const { dispatch, match, mediation, offerer } = this.props
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

    dispatch(
      requestData({
        apiPath: `/mediations${isNew ? '' : `/${get(mediation, 'id')}`}`,
        body,
        encode: 'multipart/form-data',
        handleFail: this.handleFailData,
        handleSuccess: this.handleSuccessData,
        method: isNew ? 'POST' : 'PATCH',
        stateKey: 'mediations',
      })
    )
  }

  onUrlChange = event => {
    this.setState({ inputUrl: event.target.value })
  }

  onUploadClick = event => {
    this.setState({
      image: this.$uploadInput.files[0],
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

    const $imageSections = (image || imageUrl) && (
      <Fragment>
        <div className="thumbnailManager">
          <div className="section ">
            <h2 className="has-text-primary has-text-weight-semibold active">
              Comment cadrer votre image d’accroche
            </h2>
            <ul>
              <li className="mb12">
                <span className="li-number">1</span>
                <span>
                  Le visuel doit <b>remplir le cadre 1 violet</b>.
                </span>
              </li>
              <li className="mb12">
                <span className="li-number">2</span>
                <span>
                  <b>Les éléments importants</b> (p. ex. un visage, une zone
                  d’intérêt…) doivent se situer <b>dans le cadre 2 vert.</b>
                  <br /> C’est la première vision de l'offre qu'aura
                  l'utilisateur.
                </span>
              </li>
            </ul>
            La zone en pointillés représente la partie visible de l'image dans
            la fiche détail de l’offre.
          </div>
          <div className="section">
            <div className="row">
              <div className="section">
                <h6>Exemples :</h6>
                <div className="columns crop-explain">
                  <div className="column">
                    <img
                      src="/bad-crop.png"
                      title="Exemple de cadrage"
                      alt="Explication"
                    />
                  </div>
                  <div className="column explain-text explain-bad">
                    <p>
                      <b>Mauvais cadrage</b>
                      Les éléments importants sont hors-cadre.
                    </p>
                  </div>
                  <div className="column">
                    <img
                      src="/good-crop.png"
                      title="Exemple de cadrage"
                      alt="Explication"
                    />
                  </div>
                  <div className="column explain-text explain-good">
                    <p>
                      <b>Cadrage idéal</b>
                      Les éléments importants sont visibles dans tous les
                      cadres.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <hr className="dotted" />
            <div className="row">
              <UploadThumb
                border={IMAGE_UPLOAD_BORDER}
                borderRadius={0}
                collectionName="mediations"
                entityId={get(mediation, 'id')}
                hasExistingImage={!isNew}
                height={IMAGE_UPLOAD_SIZE}
                image={image || imageUrl}
                index={0}
                width={IMAGE_UPLOAD_SIZE}
                readOnly
                required
                onImageChange={this.onImageChange}
                storeKey="mediations"
                type="thumb"
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
      </Fragment>
    )

    return (
      <Main
        name="mediation"
        backTo={{ path: backPath, label: "Revenir à l'offre" }}
        handleDataRequest={this.handleDataRequest}>
        <HeroSection title={`${isNew ? 'Créez' : 'Modifiez'} une accroche`}>
          <p className="subtitle">
            Ajoutez un visuel marquant pour mettre en avant cette offre.
          </p>
          <p>
            <b>
              L'accroche permet d'afficher votre offre "à la une" de l'app,{' '}
            </b>
            et la rend visuellement plus attrayante. C'est une image (et bientôt
            une phrase ou une vidéo) intrigante, percutante, séduisante...
            <br /> en un mot : accrocheuse.
          </p>
          <p>
            Les accroches font la spécificité du Pass Culture. Prenez le temps
            de les choisir avec soin !
          </p>
          <p>
            Le fichier doit peser <b>100Ko minimum.</b>
            <br />
            Utilisateurs avancés : vous pouvez
            <a href="https://pass.culture.fr/assets/docs/PassCulture-accroche-template-20181114.zip">
              {' '}
              télécharger ici les gabarits Illustrator et Photoshop.
            </a>
          </p>
        </HeroSection>

        <div className="section">
          <label className="label">Depuis une adresse Internet :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                type="url"
                className="input is-rounded"
                placeholder="URL du fichier"
                value={inputUrl}
                onChange={this.onUrlChange}
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

        <div className="section">
          <label className="label">...ou depuis votre poste :</label>
          <label className="button is-primary is-outlined">
            Choisir un fichier{' '}
            <input
              hidden
              onChange={this.onUploadClick}
              ref={$element => (this.$uploadInput = $element)}
              type="file"
            />
          </label>
        </div>
        {$imageSections}
      </Main>
    )
  }
}

function mapStateToProps(state, ownProps) {
  const {
    match: {
      params: { mediationId, offerId },
    },
  } = ownProps
  const offer = selectOfferById(state, offerId)
  const venue = selectVenueById(state, get(offer, 'venueId'))
  return {
    offer,
    offerer: selectOffererById(state, get(venue, 'managingOffererId')),
    mediation: selectMediationById(state, mediationId),
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withRouter,
  connect(mapStateToProps)
)(Mediation)
