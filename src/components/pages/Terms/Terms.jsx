import PropTypes from 'prop-types'
import React from 'react'
import ReactMarkdown from 'react-markdown'

import Main from '../../layout/Main'
import { LAST_DEPLOYED_COMMIT } from '../../../utils/config'

const markdownContent = `
# Titre section

## Titre Sous-section

"Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit..."
"There is no one who loves pain itself, who seeks after it and wants to have it, simply because it is pain..."
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam eget hendrerit urna, ut volutpat ligula. Aenean
egestas in erat vitae fringilla. Donec vel ante diam. Integer sit amet massa vitae sem pretium faucibus nec quis
nibh. Sed ut turpis quis odio vestibulum pulvinar. Mauris id urna turpis. Vivamus lobortis sit amet eros ut auctor.
Praesent sapien nisl, scelerisque id risus at, luctus fringilla lorem.

## Titre Sous-section

Donec fermentum at est convallis sollicitudin. Nulla maximus leo eget erat malesuada, in cursus dolor mollis.
Duis eu arcu ac leo condimentum pellentesque. In dolor neque, molestie ac ultrices ut, eleifend sit amet sapien.
Etiam congue felis nec metus fringilla mollis. Sed id sagittis diam. Vestibulum maximus nisi vel ante tempor,
eget rhoncus risus iaculis. Phasellus dolor lectus, convallis at suscipit at, viverra non ipsum. Nullam congue
laoreet lacus, eu dapibus leo.

Aenean lobortis sit amet sapien vel lobortis. Integer sagittis, sapien id accumsan facilisis, erat orci tristique
justo, a ultrices velit sem et enim. Suspendisse ut cursus nulla, id pulvinar mi. Curabitur fermentum id eros non
sollicitudin. Nullam placerat placerat urna a tempus. Cras vitae tortor erat. Nam sed ex et justo luctus consectetur
eget in massa. Phasellus nec erat tempus, luctus nisi non, placerat sapien. Vestibulum ultricies ullamcorper enim,
eget cursus nulla maximus ut. Etiam rhoncus eleifend feugiat. Curabitur ultricies ante quam, non fringilla nisl aliquam
non. Proin pharetra consectetur auctor. Proin finibus elementum sollicitudin. Maecenas ac eleifend tortor. Pellentesque
efficitur turpis id lorem maximus commodo sed vitae ipsum. Proin sed enim sapien.

Nullam molestie, enim eget consequat elementum, mi neque dictum mi, id efficitur magna lectus nec elit.
Cras quis eleifend magna. Duis iaculis lorem at tristique condimentum. Aliquam interdum nisi at pharetra
venenatis. Curabitur elementum at felis ut porttitor. Quisque volutpat tempus orci, eu egestas sem consequat
iaculis. Fusce ac convallis quam, sed consectetur sem. Aenean suscipit vel leo quis convallis. Cras posuere
lorem at nisl auctor luctus sit amet in metus. Donec eu efficitur magna, at iaculis purus. Donec nunc erat,
maximus vitae nibh ac, ultrices pharetra lorem. Vestibulum vel consectetur nulla, ac commodo arcu. Aenean vel
magna viverra, rhoncus nisi quis, ornare nisi. In rhoncus urna metus. Fusce sed posuere orci.

Donec interdum sodales ligula, faucibus imperdiet leo mattis in. Cras rhoncus, tortor vitae porta ultrices,
ex nisl imperdiet est, vitae scelerisque metus elit sit amet urna. Cras posuere pulvinar risus id sagittis.
Ut lacinia dapibus tempor. Maecenas egestas sapien non diam porta, sed porttitor orci aliquet. Fusce quis
sagittis massa. Duis eleifend iaculis urna eu lacinia. Phasellus bibendum felis in eros fermentum rhoncus.
Nam et consectetur nisl. Proin eget gravida ex. Pellentesque a leo enim. Aliquam sit amet felis arcu. Nunc
feugiat orci ut diam ullamcorper consequat.
`

const Terms = ({ lastDeployedCommit }) => (
  <Main
    backButton
    name="terms"
    noHeader
  >
    <header>
      <h1>
        {'Mentions légales'}
      </h1>
    </header>
    <div className="content">
      <ReactMarkdown source={markdownContent} />
      <div className="mt16">
        <p className="text-right">
          {`pass Culture - ${lastDeployedCommit}`}
        </p>
      </div>
    </div>
  </Main>
)

Terms.defaultProps = {
  lastDeployedCommit: LAST_DEPLOYED_COMMIT,
}

Terms.propTypes = {
  // NOTE -> `lastDeployedCommit`
  // `lastDeployedCommit` est rempli au build par le script PC
  lastDeployedCommit: PropTypes.string,
}

export default Terms
