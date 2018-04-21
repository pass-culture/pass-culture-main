import React from 'react'

const RecommendationsDebug = ({
  afterLimit,
  aroundIndex,
  beforeLimit,
  countAfterSync,
  countBeforeSync,
  isLoadingAfter,
  isLoadingBefore,
  recommendations,
}) => {
  return (
    <div className="user-mediations-debug absolute left-0 ml2 p2">
      ({isLoadingBefore ? '?' : ' '}
      {beforeLimit + 1}) {aroundIndex + 1} ({afterLimit + 1}{' '}
      {isLoadingAfter ? '?' : ' '}) / {recommendations.length + 2}
    </div>
  )
}

export default RecommendationsDebug
