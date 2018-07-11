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

import Form from './layout/Form'
import Field from './layout/Field'
import Submit from './layout/Submit'

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
        <div className='field-group'>
          <Field type='select' name='offererId' label='Structure' required options={offerers} placeholder="Sélectionnez une structure"/>
          {
            offerer && get(venues, 'length') === 0
              ? (
                <p className="errors">
                  Il faut obligatoirement une structure avec un lieu.
                </p>
              )
              :
                get(venues, 'length') > 0 && <Field type='select' name='venueId' label='Lieu' required options={venues} placeholder='Sélectionnez un lieu' />
          }
          {
            isEventType && (
              <Field type='number' name='durationMinutes' label='Durée en minutes' required />
            )
          }
        </div>
        <h2 className='pc-list-title'>Infos artistiques</h2>
        <div className='field-group'>
          <Field type='textarea' name='description' label='Description' maxLength={750} required isExpanded />
          <Field name='author' label='Auteur' isExpanded />
          {
            isEventType && [
              <Field key={0} name='stageDirector' label='Metteur en scène' isExpanded />,
              <Field key={1} name='performer' label='Interprète' isExpanded />
            ]
          }
        </div>
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
