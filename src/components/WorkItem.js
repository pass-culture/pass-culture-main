import classnames from 'classnames'
import React from 'react'

import { API_URL } from '../utils/config'

const WorkItem = ({ composer,
  id,
  extraClass,
  name,
  performer
}) => {
  return (
    <div className={classnames('work-item col-9 mx-auto flex items-center justify-center p2',
      { [extraClass]: extraClass })}>
      <img alt='thumbnail'
        className='offer-form__content__img mb1 mr2'
        src={`${API_URL}/thumbs/${id}`} />
      <div>
        <div className='h2 mb1 left-align'>
          {name}
        </div>
        <div className='left-align'>
          {composer} {performer}
        </div>
      </div>
    </div>
  )
}

export default WorkItem
