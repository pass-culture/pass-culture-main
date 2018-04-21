import classnames from 'classnames'
import React from 'react'

import { THUMBS_URL } from '../../utils/config'

const ThingItem = ({
  composer,
  id,
  identifier,
  extraClass,
  name,
  performer,
  type,
}) => {
  return (
    <div
      className={classnames(
        'thing-item col-9 mx-auto flex items-center justify-center p2',
        { [extraClass]: extraClass }
      )}
    >
      <img
        alt="thumbnail"
        className="thing-item__content__img mr2"
        src={`${THUMBS_URL}/things/${id}`}
      />
      <div>
        <div className="thing-item__content__id left-align mb1">
          {type} {identifier}
        </div>
        <div className="h2 mb1 left-align">{name}</div>
        <div className="left-align">
          {composer} {performer}
        </div>
      </div>
    </div>
  )
}

export default ThingItem
