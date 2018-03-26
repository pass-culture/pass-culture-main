import React from 'react'

const UserMediationsDebug = ({ afterLimit,
  aroundIndex,
  beforeLimit,
  countAfterSync,
  countBeforeSync,
  isLoadingAfter,
  isLoadingBefore,
  userMediations
}) => {

  return (
    <div className='user-mediations-debug absolute left-0 ml2 p2'>
        ({isLoadingBefore ? '?' : ' '}{beforeLimit}) {aroundIndex + 1} ({afterLimit} {isLoadingAfter ? '?' : ' '}) / {userMediations.length}
    </div>
  )
}

export default UserMediationsDebug
