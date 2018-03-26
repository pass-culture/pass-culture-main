import React from 'react'

const UserMediationsDebug = ({ aroundIndex,
  countAfterSync,
  countBeforeSync,
  isLoadingAfter,
  isLoadingBefore,
  userMediations
}) => {
  return (
    <div className='user-mediations-debug absolute left-0 ml2 p2'>
        ({isLoadingBefore ? '?' : ' '}{countBeforeSync}) {aroundIndex + 1} ({userMediations.length + 1 - countAfterSync} {isLoadingAfter ? '?' : ' '}) / {userMediations.length}
    </div>
  )
}

export default UserMediationsDebug
