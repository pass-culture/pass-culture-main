import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import OccasionForm from '../OccasionForm'
import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { resetForm } from '../../reducers/form'
import { closeModal, showModal } from '../../reducers/modal'
import { showNotification } from '../../reducers/notification'
import selectOccasionForm from '../../selectors/occasionForm'
import selectSelectedType from '../../selectors/selectedType'
import { eventNormalizer } from '../../utils/normalizers'


class OccasionPage extends Component {
  constructor () {
    super()
    this.state = {
      isReadOnly: true,
      hasNoVenue: false
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      currentMediation,
      location: { search },
      isNew,
      occasionForm
    } = nextProps
    const {
      id
    } = (currentMediation || {})
    const {
      isEventType
    } = (occasionForm || {})
    const isEdit = search === '?modifie'
    const isReadOnly = !isNew && !isEdit
    const apiPath = isEventType
      ? `events${id ? `/${id}` : ''}`
      : `things${id ? `/${id}` : ''}`
    return {
      apiPath,
      isReadOnly
    }
  }

  handleRequestData = () => {
    const {
      history,
      requestData,
      showModal,
      user
    } = this.props

    if (!user) {
      return
    }

    requestData(
      'GET',
      'offerers',
      {
        handleSuccess: (state, action) => !get(state, 'data.venues.length')
          && showModal(
            <div>
              Vous devez avoir déjà enregistré un lieu
              dans une de vos structures pour ajouter des offres
            </div>,
            {
              onCloseClick: () => history.push('/structures')
            }
          ),
        normalizer: { managedVenues: 'venues' }
      }
    )
    requestData('GET', 'types')
  }

  handleSuccessData = (state, action) => {
    const {
      data,
      method
    } = action
    const {
      closeModal,
      history,
      occasionForm,
      showModal,
      showNotification
    } = this.props
    const {
      isEventType
    } = (occasionForm || {})

    // PATCH
    if (method === 'PATCH') {
      history.push('/offres')
      showNotification({
        text: 'Votre offre a bien été enregistrée',
        type: 'success'
      })
      return
    }

    // POST
    if (method === 'POST') {
      // switch to the path with the new created id
      const routePath = `/offres/${isEventType ? 'evenements' : 'objets'}/${data.id}`

      // modal
      isEventType && showModal(
        <div>
          Cette offre est-elle soumise à des dates ou des horaires particuliers ?
          <NavLink
            className='button'
            to={`${routePath}/dates`}
          >
            Oui
          </NavLink>
          <button onClick={() => { closeModal(); history.push('/offres') }}
            className='button'>
            Non
          </button>
        </div>
      )
    }
  }

  componentDidMount () {
    this.handleRequestData()
  }

  componentDidUpdate (prevProps) {
    const {
      user
    } = this.props
    if (prevProps.user !== user) {
      this.handleRequestData()
    }
  }

  componentWillUnmount () {
    this.props.resetForm()
  }


  render () {
    const {
      currentOccasion,
      isLoading,
      isNew,
      location: { pathname },
      occasionIdOrNew,
      occasionForm,
      routePath,
      selectedType,
      typeOptions,
    } = this.props
    const {
      event,
      thing
    } = (currentOccasion || {})
    console.log('currentOccasion', currentOccasion, 'selectedType', selectedType)
    const {
      id,
      name
    } = (event || thing || {})
    const {
      isEventType,
      requiredFields
    } = (occasionForm || {})
    const {
      apiPath,
      isReadOnly
    } = this.state

    const typeOptionsWithPlaceholder = get(typeOptions, 'length') > 1
      ? [{ label: "Sélectionnez un type d'offre" }].concat(typeOptions)
      : typeOptions

    return (
      <PageWrapper
        backTo={{path: '/offres', label: 'Vos offres'}}
        name='offer'
        loading={isLoading}
      >
        <div className='section'>
          <h1 className='pc-title'>
            {
              isNew
                ? 'Ajouter'
                : 'Modifier'
            } une offre
          </h1>
          <p className='subtitle'>
            Renseignez les détails de cette offre et mettez-la en avant en ajoutant une ou plusieurs accorches.
          </p>
          <FormField
            collectionName='occasions'
            defaultValue={name}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Titre de l'offre:" />}
            name="name"
            readOnly={isReadOnly}
            required={!isReadOnly}
          />
          <FormField
            collectionName='occasions'
            defaultValue={selectedType}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Type :" />}
            name="type"
            options={typeOptionsWithPlaceholder}
            readOnly={isReadOnly}
            required={!isReadOnly}
            type="select"
          />
        </div>
        {
          selectedType && <OccasionForm {...this.props} />
        }

        <hr />
        <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
          <div className="control">
            {
              isReadOnly
                ? (
                  <NavLink to={`${pathname}?modifie`} className='button is-secondary is-medium'>
                    Modifier l'offre
                  </NavLink>
                )
                : (
                  <NavLink
                    className="button is-secondary is-medium"
                    to='/offres'>
                    Annuler
                  </NavLink>
                )
            }
          </div>
          <div className="control">
            {
              isReadOnly
                ? (
                  <NavLink to={routePath} className='button is-primary is-medium'>
                    Terminer
                  </NavLink>
                )
                : (
                  <SubmitButton
                    className="button is-primary is-medium"
                    getBody={form => {
                      const occasionForm = get(form, `occasionsById.${occasionIdOrNew}`)
                      // remove the EventType. ThingType.
                      if (occasionForm.type) {
                        occasionForm.type = occasionForm.type.split('.')[1]
                      }
                      return occasionForm
                    }}
                    getIsDisabled={form => {
                      if (!requiredFields) {
                        return true
                      }
                      const missingFields = requiredFields.filter(r =>
                        !get(form, `occasionsById.${occasionIdOrNew}.${r}`))
                      return isNew
                        ? missingFields.length > 0
                        : missingFields.length === requiredFields.length
                    }}
                    handleSuccess={this.handleSuccessData}
                    normalizer={eventNormalizer}
                    method={isNew ? 'POST' : 'PATCH'}
                    path={apiPath}
                    storeKey="events"
                    text="Enregistrer"
                  />
                )
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
    (state, ownProps) => ({
      occasionForm: selectOccasionForm(state, ownProps),
      selectedType: selectSelectedType(state, ownProps),
      typeOptions: state.data.types
    }),
    {
      closeModal,
      resetForm,
      showModal,
      showNotification
    }
  )
)(OccasionPage)
