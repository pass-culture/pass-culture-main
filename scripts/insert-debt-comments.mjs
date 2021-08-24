import fs from 'fs'

import countLinesInFile from 'count-lines-in-file'
import glob from 'glob'
import minimatch from 'minimatch'
import prependFile from 'prepend-file'

const comment = (text) => `/*
* @debt ${text}
*/
`

const insertComments = [
  {
    match: 'from \'react-final-form\'',
    comment: 'deprecated "Gaël: deprecated usage of react-final-form"'
  },{
    match: 'from \'components/layout/form',
    comment: 'deprecated "Gaël: deprecated usage of react-final-form custom fields"'
  },{
    match: 'from \'redux-saga',
    comment: 'deprecated "Gaël: deprecated usage of redux-saga-data"'
  },{
    match: 'from \'enzyme\'',
    comment: 'rtl "Gaël: migration from enzyme to RTL"'
  },{
    match: 'extends Component',
    comment: 'standards "Gaël: migration from classes components to function components"'
  },{
    match: 'extends React.Component',
    comment: 'standards "Gaël: migration from classes components to function components"'
  },{
    match: 'extends PureComponent',
    comment: 'standards "Gaël: migration from classes components to function components"'
  },{
    match: 'extends React.PureComponent',
    comment: 'standards "Gaël: migration from classes components to function components"'
  },
]

const isPathTooDeep = (filePath) => {
  const directories = filePath.replace('./', '').split('/')
  directories.splice(-1)
  return directories.length > 6
}

glob("./src/**/*.{js,jsx,scss}", {}, (er, files) => {
  if (er) throw er
  
  files.forEach((file) => {
    const comments = []
    const data = fs.readFileSync(file)

    countLinesInFile(file, (err, linesCount) => {
      if (err) throw err
      if (linesCount > 300) {
        comments.push('complexity "Gaël: file over 300 lines"')
      }
    })

    if (isPathTooDeep(file)) {
      comments.push('complexity "Gaël: file nested too deep in directory structure"')
    }

    if (minimatch(file, './src/styles/{components|global}/**/*.scss')) {
      comments.push('directory "Gaël: SCSS file should be co-located and imported within a component"')
    }

    if (minimatch(file, './src/components/pages/Styleguide/**/*.jsx')) {
      comments.push('directory "Gaël: this file should be migrated within storybook"')
    }

    if (
      minimatch(file, './src/components/**/!(__specs__)/*.jsx')
      && !minimatch(file, './src/components/pages/Styleguide/**/*.jsx')
    ) {
      comments.push('directory "Gaël: this file should be migrated within the new directory structure"')
    }

    if (minimatch(file, './src/components/hoc/**/!(__specs__)/*.js')) {
      comments.push('standard "Gaël: HOC should be replaced in favor of hooks"')
    }

    insertComments.forEach((useCase) => {
      if (data.indexOf(useCase.match) >= 0) {
        comments.push(useCase.comment)
      }
    })

    if (comments.length > 0) {
      console.log('---------------')
      console.log(file)
      console.log(comments)
      //prependFile(file, comments.map(text => comment(text)).join('n/'))
    }
  })
})