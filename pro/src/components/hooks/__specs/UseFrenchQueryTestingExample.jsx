import React, { Fragment, useEffect, useState } from 'react'

import useFrenchQuery from 'components/hooks/useFrenchQuery'

export const UseFrenchQueryTestingExample = () => {
  const [queryChangeCount, setQueryChangeCount] = useState(0)
  const [setterIdentityCount, setSetterIdentityCount] = useState(0)
  const [newQueryParams, setNewQueryParams] = useState({})

  const [query, setQuery] = useFrenchQuery()

  useEffect(() => {
    setQueryChangeCount(renderCount => renderCount + 1)
  }, [query])

  useEffect(() => {
    setSetterIdentityCount(setterIdentitiesCount => setterIdentitiesCount + 1)
  }, [setQuery])

  const handleChange = queryParamName => event => {
    event.persist()
    setNewQueryParams(newQueryParams => ({
      ...newQueryParams,
      [queryParamName]: event.target.value,
    }))
  }

  const handleClick = () => () => {
    setQuery(newQueryParams)
  }

  const queryParams = Object.entries(query)
  return (
    <>
      {queryParams.map(([queryParamName, queryParamValue]) => (
        <Fragment key={queryParamName}>
          <div>{`${queryParamName}: ${queryParamValue}`}</div>
          <label>
            {queryParamName}
            <input onChange={handleChange(queryParamName)} type="text" />
          </label>
        </Fragment>
      ))}
      <button onClick={handleClick()} type="button">
        Update query params
      </button>
      <div>{`Number of query changes: ${queryChangeCount}`}</div>
      <div>{`Number of setter identities: ${setterIdentityCount}`}</div>
    </>
  )
}
