import React from 'react'
import { connect } from 'react-redux'

import Card from './Card'
import Loading from './Loading'

const Cards = ({
  elements,
  isLoadingActive,
  state
}) => {
  return  !isLoadingActive && elements && elements.length > 0
      ? elements.map((element, index) =>
          <Card {...state}
            index={index}
            itemsCount={elements.length}
            key={index}
            {...element}
            {...element.mediation && element.mediation.offer}
            {...element.offer} />
        )
      : (
        <div className='card flex items-center justify-center'>
          <Loading />
        </div>
      )
}

export default connect(
  state => ({ isLoadingActive: state.loading.isActive })
)(Cards)
