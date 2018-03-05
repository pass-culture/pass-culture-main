import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { Carousel } from 'react-responsive-carousel'

import Card from './Card'
import LastCard from './LastCard'
import LoadingCard from './LoadingCard'
import SearchInput from '../components/SearchInput'

class Explorer extends Component {
  componentDidMount () {
    const newState = {
      carouselElement: this.carouselElement,
      carousselNode: findDOMNode(this.carouselElement),
    }
    if (Object.keys(newState).length > 0) {
      this.setState(newState)
    }
  }
  render () {
    const { cards,
      firstCard,
      firstNotReadItem,
      hasPushPullRequested,
      isFading,
      isLast,
      isNewReading,
      isReordering,
      loadingTag,
      onChange,
      searchCollectionName,
      searchHook,
      selectedCard,
      selectedItem
    } = this.props
    /*
    console.log(cards &&
      cards.map(({ id, dateUpdated, dateRead }) =>
        ({ id, dateUpdated, dateRead })))
    */
    return (
      <div className='explorer mx-auto p2' id='explorer'>
        <div className='explorer__search absolute'>
          <SearchInput collectionName={searchCollectionName}
            hook={searchHook} />
        </div>
        {
          !isReordering
            ? (
              <Carousel axis='horizontal'
                emulateTouch
                ref={element => this.carouselElement = element}
                selectedItem={selectedItem}
                showArrows={!isFading && !isReordering && !isNewReading && !hasPushPullRequested}
                swipeScrollTolerance={100}
                showStatus={false}
                showIndicators={false}
                showThumbs={false}
                transitionTime={250}
                onChange={onChange} >
                {
                  loadingTag !== 'search' && cards && cards.length > 0
                    ? ((!firstCard && [<LoadingCard key='first' isForceActive />]) || [])
                      .concat(
                        cards.map((card, index) =>
                          <Card {...this.state}
                            cardsLength={cards.length}
                            index={index}
                            isHidden={isFading}
                            key={index}
                            {...card}
                          />
                        )).concat([
                          firstNotReadItem === -1
                            ? <LastCard key='last' />
                            : <LoadingCard key='next' isForceActive />
                        ])
                    : <LoadingCard />
                }
              </Carousel>
            )
          : (
            <div className='carousel'>
              <LoadingCard isForceActive />
            </div>
          )
        }
      </div>
    )
  }
}

export default Explorer
