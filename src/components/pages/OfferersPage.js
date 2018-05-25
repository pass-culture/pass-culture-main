import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import get from 'lodash.get'
import { AutoSizer, List } from 'react-virtualized'


import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'
import OffererItem from '../OffererItem'
import SearchInput from '../layout/SearchInput'

class OfferersPage extends Component {


  render() {
    const {
      offerers
    } = this.props
    return (
      <PageWrapper name="profile" loading={!offerers}>
        <h1 className="title has-text-centered">Vos lieux</h1>
        <nav className="level is-mobile">
          <NavLink to={`/lieux/nouveau`}>
            <button className="button is-primary level-item">
              Nouveau lieu
            </button>
          </NavLink>
        </nav>
        <nav className="level is-mobile">
          <SearchInput collectionNames={["events", "things"]} isLoading />
        </nav>
        <div className="offerers-list">
          <AutoSizer>
          {
            ({width, height}) => offerers && offerers.length
              ? <List
                height={height}
                rowCount={offerers.length}
                rowHeight={190}
                rowRenderer={({ index, key, style }) => (
                  <div key={index} style={style}>
                    <OffererItem {...offerers[index]} />
                  </div>
                )}
                width={width}
              />
              : ''
          }
          </AutoSizer>
        </div>
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter,
  connect(
    state => ({
      user: get(state, 'data.users.0'),
      offerers: get(state, 'user.offerers')
    }),
    { requestData }
  )
)(OfferersPage)