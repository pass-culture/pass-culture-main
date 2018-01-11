import classnames from 'classnames'
import React, { Component }  from 'react'
import { connect } from 'react-redux'

import EditSellerFavorite from './EditSellerFavorite'
import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import PriceItem from './PriceItem'
import SellerFavorite from './SellerFavorite'
import SubmitButton from './SubmitButton'

class EditOffer extends Component {
  constructor () {
    super ()
    this.state = {
      isEditSellerFavorite: false,
      isNewPrice: false
    }
  }
  onAddFavoriteClick = () => {
    this.setState({ isEditSellerFavorite: true })
  }
  onSubmitFavoriteClick = () => {
    this.setState({ isEditSellerFavorite: false })
  }
  onAddPriceClick = () => {
    console.log('qsdqs')
  }
  render () {
    const { description,
      id,
      isEditing,
      isNewPrice,
      name,
      sellersFavorites,
      thumbnailUrl,
      prices,
      work
    } = this.props
    const { isEditSellerFavorite } = this.state
    console.log('isEditing', isEditing)
    return (
      <div className='edit-offer p2'>

        <FormInput className='input mt1 mb3'
          defaultValue={name}
          name='name'
          placeholder="titre de l'offre"
        />
        <div className='sep mb2' />
        <div className='edit-offer__hero flex flex-wrap items-center justify-around mb2 p1'>
          <img alt='thumbnail'
            className='edit-offer__hero__img mb1'
            src={thumbnailUrl || work.thumbnailUrl} />
          <FormTextarea className='textarea edit-offer__hero__textarea'
            defaultValue={description}
            name='description'
            placeholder="Vous pouvez écrire un description ici" >
            {description}
          </FormTextarea>
        </div>

        <div className='sep mb2' />

        {
          sellersFavorites && sellersFavorites.length
            ? (
              <div className='mb2'>
                <div className='h2 mb2'>
                  Coups de Coeur
                </div>

                <div className='flex items-center flex-start mb2'>
                  {
                    isEditSellerFavorite
                    ? <SubmitButton className={classnames('button button--alive', {
                          'hide': isEditing
                        })}
                        getBody={form => [{
                          description: form.sellersFavoriteDescription,
                          offerId: id
                        }] }
                        getOptimistState={(state, action) => {
                          let sellersFavorites
                          const offers = state.offers.map(offer => {
                            if (offer.id === id) {
                              /*
                              offer.sellersFavorites = action.config.body.concat(
                                offer.sellersFavorites)
                              */
                              sellersFavorites = action.config.body.concat(
                                offer.sellersFavorites)
                            }
                            return offer
                          })
                          return {
                            // offers,
                            sellersFavorites
                          }
                        }}
                        onClick={this.onSubmitFavoriteClick}
                        path='sellersFavorites'
                        text='Ajouter' />
                    : (
                        <button className={classnames(
                            'button button--alive button--rounded left-align',
                            { 'hide': isEditing }
                          )}
                          onClick={this.onAddFavoriteClick}>
                          +
                        </button>
                    )
                  }
                </div>
                { isEditSellerFavorite && <EditSellerFavorite offerId={id} /> }
                {
                  sellersFavorites && sellersFavorites.map((favorite, index) => (
                    <SellerFavorite key={index} {...favorite} />
                  ))
                }
              </div>
            )
            : (
              <button className='button button--alive mb2'
                onClick={this.onAddFavoriteClick}
              >
                Ajouter des Coups de Coeur ?
              </button>
            )
        }

        <div className='sep mb2' />

        <div className='h2 mb2'>
          Offres
        </div>
        <div className='flex items-center flex-start mb1 col-9 mx-auto'>
          <button className='button button--alive button--rounded'
            onClick={this.onAddPriceClick} >
            +
          </button>
        </div>
        {
          prices && prices.map((price, index) => (
            <PriceItem key={index} {...price} />
          ))
        }

        <div className='sep mb2' />

        <button className='button button--alive mb2'>
          Soumettre
        </button>
      </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({
    isEditing: Object.keys(state.form).length > 0,
    sellersFavorites: state.request.sellersFavorites || ownProps.sellersFavorites
  })
)(EditOffer)
