import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import MediationManager from './MediationManager'
import OccurenceManager from './OccurenceManager'
import Icon from './layout/Icon'
import FormField from './layout/FormField'
import Label from './layout/Label'
import { mergeForm } from '../reducers/form'
import { closeModal, showModal } from '../reducers/modal'
import createOccurencesSelector from '../selectors/createOccurences'
import createTypesSelector from '../selectors/createTypes'
import { pluralize } from '../utils/string'
import { optionify } from '../utils/form'

class OccasionForm extends Component {

  handleShowOccurencesModal = () => {
    const {
      occasion,
      history,
      match: { params: { modalType } },
      routePath,
      showModal
    } = this.props

    if (modalType !== 'dates') {
      return
    }

    showModal(
      <OccurenceManager occasion={occasion} />,
      {
        onCloseClick: () => history.push(routePath)
      }
    )

  }

  componentDidMount () {
    this.handleShowOccurencesModal()
  }

  componentDidUpdate (prevProps) {
    const {
      match: { params: { modalType } }
    } = this.props
    if (!get(prevProps, 'match.params.modalType') && modalType === 'dates') {
      this.handleShowOccurencesModal()
    }
  }

  render () {
    const {
      event,
      isEventType,
      isNew,
      isReadOnly,
      occasionIdOrNew,
      occurences,
      offerer,
      offerers,
      routePath,
      thing,
      user,
      venue,
      venues,
    } = this.props
    const {
      author,
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      mediaUrls,
      performer,
      stageDirector,
    } = (event || thing || {})

    return (
      <div>
        {
          !isNew && (
            <div className='field'>
            {
              isEventType && (
                <div className='field form-field is-horizontal'>
                  <div className='field-label'>
                    <label className="label" htmlFor="input_occasions_name">
                      <div className="subtitle">Dates :</div>
                    </label>
                  </div>
                  <div className='field-body'>
                    <div className='field'>
                      <div className='nb-dates'>
                        {pluralize(get(occurences, 'length'), 'date')}
                      </div>
                      <NavLink
                        className='button is-primary is-outlined is-small'
                        to={`${routePath}/dates`}
                      >
                        <span className='icon'><Icon svg='ico-calendar' /></span>
                        <span>Gérer les dates</span>
                      </NavLink>
                    </div>
                  </div>
                </div>
              )
            }
            <MediationManager />
          </div>
          )
        }
        <h2 className='pc-list-title'>
          Infos pratiques
        </h2>
        {
          /*
          <FormField
            collectionName='occasions'
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Prix:" />}
            name="price"
            readOnly={isReadOnly}
          />
          <FormField
            className='column'
            collectionName='occasions'
            entityId={occasionIdOrNew}
            inputClassName='input is-rounded'
            label={<Label title="Gratuit" />}
            name="isForFree"
            readOnly={isReadOnly}
            type="checkbox"
          />
          */
        }
        <FormField
          collectionName='occasions'
          defaultValue={get(offerer, 'id')}
          entityId={occasionIdOrNew}
          isHorizontal
          label={<Label title="Structure :" />}
          required
          name='offererId'
          options={optionify(offerers, 'Sélectionnez une structure')}
          readOnly={isReadOnly || !isNew}
          type="select"
        />
        {
          offerer && get(venues, 'length') === 0
            ? (
              <p>
                Il faut obligatoirement une structure avec un lieu.
              </p>
            )
            :
              get(venues, 'length') > 0 && <FormField
                collectionName='occasions'
                defaultValue={get(venue, 'id')}
                entityId={occasionIdOrNew}
                isHorizontal
                label={<Label title="Lieu :" />}
                name='venueId'
                options={optionify(venues, 'Sélectionnez un lieu')}
                readOnly={isReadOnly || !isNew}
                required={!isReadOnly}
                type="select"
              />
        }
        {
          isEventType && (
            <FormField
              collectionName='occasions'
              defaultValue={durationMinutes}
              entityId={occasionIdOrNew}
              isHorizontal
              label={<Label title="Durée (en minutes) :" />}
              name="durationMinutes"
              readOnly={isReadOnly}
              required={!isReadOnly}
              type="number"
            />
          )
        }

        <h2 className='pc-list-title'>Infos artistiques</h2>
        <FormField
          collectionName='occasions'
          defaultValue={description}
          entityId={occasionIdOrNew}
          isHorizontal
          isExpanded
          label={<Label title="Description :" />}
          name="description"
          readOnly={isReadOnly}
          required={!isReadOnly}
          type="textarea"
        />
        <FormField
          collectionName='occasions'
          defaultValue={author}
          entityId={occasionIdOrNew}
          isHorizontal
          isExpanded
          label={<Label title="Auteur :" />}
          name="author"
          readOnly={isReadOnly}
        />
        {
          isEventType && [
            <FormField
              collectionName='occasions'
              defaultValue={stageDirector}
              entityId={occasionIdOrNew}
              isHorizontal
              isExpanded
              key={0}
              label={<Label title="Metteur en scène:" />}
              name="stageDirector"
              readOnly={isReadOnly}
            />,
            <FormField
              collectionName='occasions'
              defaultValue={performer}
              entityId={occasionIdOrNew}
              isHorizontal
              isExpanded
              key={1}
              label={<Label title="Interprète:" />}
              name="performer"
              readOnly={isReadOnly}
            />
          ]
        }

      { false && [
        <h2 className='pc-list-title'>Contact</h2>,
        <FormField
          collectionName='occasions'
          defaultValue={contactName || get(user, 'publicName')}
          entityId={occasionIdOrNew}
          isHorizontal
          isExpanded
          label={<Label title="Nom du contact :" />}
          name="contactName"
          readOnly={isReadOnly}
          required={!isReadOnly}
        />,
        <FormField
          collectionName='occasions'
          defaultValue={contactEmail || get(user, 'email')}
          entityId={occasionIdOrNew}
          isHorizontal
          isExpanded
          label={<Label title="Email de contact :" />}
          name="contactEmail"
          readOnly={isReadOnly}
          required={!isReadOnly}
          type="email"
        />,
        <FormField
          collectionName='occasions'
          defaultValue={contactPhone}
          entityId={occasionIdOrNew}
          isHorizontal
          label={<Label title="Tel de contact :" />}
          name="contactPhone"
          readOnly={isReadOnly}
        />,
        ]}
        {false && <FormField
                    collectionName='occasions'
                    defaultValue={mediaUrls}
                    entityId={occasionIdOrNew}
                    label={<Label title="Media URLs" />}
                    name="mediaUrls"
                    readOnly={isReadOnly}
                    type="list"
                  />}


      </div>
    )
  }
}

const occurencesSelector = createOccurencesSelector()
const typesSelector = createTypesSelector()

export default connect(
  (state, ownProps) => {
    const eventId = get(ownProps, 'occasion.eventId')
    const venueId = get(ownProps, 'occasion.venueId')
    return {
      occurences: occurencesSelector(state, venueId, eventId),
    }
  },
  {
    closeModal,
    mergeForm,
    showModal
  }
)(OccasionForm)
