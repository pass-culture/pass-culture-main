import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { createSelector } from 'reselect'

import DeleteButton from './DeleteButton'
import OfferForm from './OfferForm'
import OfferJoinForm from './OfferJoinForm'
import SubmitButton from '../components/SubmitButton'
import WorkItem from './WorkItem'
import { assignData } from '../reducers/data'
import { closeModal } from '../reducers/modal'
import { NEW } from '../utils/config'

class OfferModify extends Component {
  onCloseClick = () => {
    this.props.closeModal()
  }
  componentWillUnmount () {
    this.props.assignData({ modifyOfferId: null })
  }
  render () {
    const { id, work } = this.props
    const isNew = id === NEW
    return (
      <div className='offer-modify p2'>
        <div className='h2 mt2 mb2'> Offre </div>
        <WorkItem extraClass='mb2' {...work} />
        <OfferForm {...this.props} />
        <div>
          <SubmitButton add='append'
            extraClass='mr1'
            getBody={form => form.offersById[id]}
            getIsDisabled={form =>
              !form ||
              !form.offersById ||
              !form.offersById[id] ||
              (
                !form.offersById[id].description &&
                !form.offersById[id].name
              )
            }
            getOptimistState={(state, action) => {
              const modifyOffer = Object.assign({ id,
                work
              }, action.config.body)
              return { offers: state.offers.concat(modifyOffer) }
            }}
            getSuccessState={(state, action) => {
              if (action.method === 'POST') {
                return { modifyOfferId: action.data.id }
              }
            }}
            method={isNew ? 'POST' : 'PUT'}
            path='offers'
            text={isNew ? 'Enregistrer' : 'Modifer'}
          />
          <DeleteButton className={classnames('button button--alive mb2', {
            'button--disabled': isNew
          })}
            collectionName='offers'
            disabled={isNew}
            id={id}
            text='Supprimer'
          />
        </div>
        {
          !isNew && [
            <OfferJoinForm {...this.props} />,
            <button className='button button--alive'
              onClick={this.onCloseClick} >
              Ok
            </button>
          ]
        }
      </div>
    )
  }
}

OfferModify.defaultProps = {
  id: NEW
}

const getModifyOffer = createSelector(state => state.data.offers,
  (state, ownProps) =>
    state.data.modifyOfferId || ownProps.id,
  (offers, offerId) => offers.find(({ id }) => id === offerId)
)

export default connect(
  (state, ownProps) => getModifyOffer(state, ownProps) || {},
  { assignData, closeModal }
)(OfferModify)
