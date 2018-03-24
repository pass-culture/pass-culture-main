import React from 'react'

const UserMediationsDebug = ({ aroundIndex,
  countAfterSync,
  countBeforeSync,
  userMediations
}) => {
  return (
    <div className='user-mediations-debug absolute left-0 ml2 p2'>
        ({countBeforeSync}) {aroundIndex + 1} ({userMediations.length - countAfterSync}) / {userMediations.length}
    </div>
  )
}

export default UserMediationsDebug
