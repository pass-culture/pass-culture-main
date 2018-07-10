import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import OccurenceManager from './OccurenceManager'
import FormField from './layout/FormField'
import Label from './layout/Label'
import { mergeForm } from '../reducers/form'
import { closeModal, showModal } from '../reducers/modal'
import occurencesSelector from '../selectors/occurences'
import { optionify } from '../utils/form'

class OccasionForm extends Component {

  handleShowOccurencesModal = () => {
    const {
      history,
      location,
      match,
      occasion,
      occurences,
      showModal
    } = this.props
    const { params: { feature } } = match
    if (feature !== 'dates') {
      return
    }
    showModal(
      <OccurenceManager
        history={history}
        location={location}
        match={match}
        occasion={occasion}
        occurences={occurences}
      />,
      {
        isUnclosable: true
      }
    )
  }

  componentDidMount () {
    this.handleShowOccurencesModal()
  }

  componentDidUpdate (prevProps) {
    const {
      match: { params: { feature } },
      location: { pathname },
      occasion,
      occurences
    } = this.props
    if (feature === 'dates') {
      if (
        !get(prevProps, 'match.params.feature') ||
        prevProps.occasion !== occasion ||
        prevProps.occurences !== occurences ||
        prevProps.location.pathname !== pathname
      ) {
        this.handleShowOccurencesModal()
      }
    }
  }

  render () {
    const {
      event,
      isEventType,
      isNew,
      isReadOnly,
      occasionIdOrNew,
      offerer,
      offerers,
      thing,
      user,
      venue,
      venues,
    } = this.props
    const {
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      extraData,
      mediaUrls
    } = (event || thing || {})
    const {
      author,
      performer,
      stageDirector
    } = (extraData || {})

    return (
      <div>
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
        <div className='field-group'>
          <FormField
            collectionName='occasions'
            defaultValue={get(offerer, 'id')}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Structure :" />}
            name='offererId'
            options={optionify(offerers, 'Sélectionnez une structure')}
            readOnly={isReadOnly || !isNew}
            required={!isReadOnly}
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
                label={<Label title="Durée en minutes :" />}
                name="durationMinutes"
                readOnly={isReadOnly}
                required={!isReadOnly}
                type="number"
              />
            )
          }
        </div>
        <h2 className='pc-list-title'>Infos artistiques</h2>
        <div className='field-group'>
          <FormField
            collectionName='occasions'
            defaultValue={description}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Description :" />}
            maxLength={750}
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
        </div>
      { false && [
        <h2 className='pc-list-title'>Contact</h2>,
        <div className='field-group'>
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
          /></div>,
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

export default compose(
  withRouter,
    connect(
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
  )
)(OccasionForm)
