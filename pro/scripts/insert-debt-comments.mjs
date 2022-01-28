#! /usr/bin/env node
import fs from 'fs'

import glob from 'glob'
import minimatch from 'minimatch'
import prependFile from 'prepend-file'

import eslintOutput from './eslintoutput.mjs'

const comment = text => `* @debt ${text}`

const filteredEslintOutput = eslintOutput
  .filter(fileOutput => fileOutput.errorCount + fileOutput.warningCount > 0)
  .map(fileOutput => {
    const rules = fileOutput.messages.map(message =>
      message.ruleId.startsWith('testing-library/')
        ? 'testing-library'
        : message.ruleId
    )

    return {
      filePath: fileOutput.filePath.replace(
        '/Users/gael.boyenval/dev/pass-culture-main/pro/',
        './'
      ),
      messages: [...new Set(rules)],
    }
  })

const insertComments = [
  {
    match: "from 'react-final-form'",
    comment: 'deprecated "Gaël: deprecated usage of react-final-form"',
  },
  {
    match: "from 'components/layout/form",
    comment:
      'deprecated "Gaël: deprecated usage of react-final-form custom fields"',
  },
  {
    match: "from 'redux-saga",
    comment: 'deprecated "Gaël: deprecated usage of redux-saga-data"',
  },
  {
    match: 'import { withRouter }',
    comment:
      'standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"',
  },
  {
    match: 'import { connect }',
    comment:
      'standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"',
  },
  {
    match: 'withQueryRouter',
    comment: 'deprecated "Gaël: deprecated usage of withQueryRouter"',
  },
  {
    match: "from 'enzyme'",
    comment: 'rtl "Gaël: migration from enzyme to RTL"',
  },
  {
    match: 'extends Component',
    comment:
      'standard "Gaël: migration from classes components to function components"',
  },
  {
    match: 'extends React.Component',
    comment:
      'standard "Gaël: migration from classes components to function components"',
  },
  {
    match: 'extends PureComponent',
    comment:
      'standard "Gaël: migration from classes components to function components"',
  },
  {
    match: 'extends React.PureComponent',
    comment:
      'standard "Gaël: migration from classes components to function components"',
  },
  {
    match: 'await act(',
    comment: 'rtl "Gaël: bad use of act in testing library"',
  },
]

const isPathTooDeep = filePath => {
  const directories = filePath.replace('./', '').split('/')
  directories.splice(-1)
  return directories.length > 6
}

glob('./src/**/*.{js,jsx,scss}', {}, (er, files) => {
  if (er) throw er

  files.forEach(file => {
    const comments = []
    const data = fs.readFileSync(file)
    const relatedEslintErrors = filteredEslintOutput.find(
      eslintFile => eslintFile.filePath === file
    )
    const relatedFileMessages = relatedEslintErrors?.messages

    if (relatedFileMessages) {
      if (relatedFileMessages.includes('max-lines')) {
        comments.push('complexity "Gaël: file over 300 lines"')
      }

      if (
        relatedFileMessages.includes('max-lines-per-function') ||
        relatedFileMessages.includes('max-statements') ||
        relatedFileMessages.includes('max-nested-callbacks') ||
        relatedFileMessages.includes('complexity') ||
        relatedFileMessages.includes('max-params')
      ) {
        comments.push(
          'complexity "Gaël: the file contains eslint error(s) based on our new config"'
        )
      }

      if (relatedFileMessages.includes('testing-library')) {
        comments.push(
          'rtl "Gaël: this file contains eslint error(s) based on eslint-testing-library plugin"'
        )
      }
    }

    if (isPathTooDeep(file)) {
      comments.push(
        'complexity "Gaël: file nested too deep in directory structure"'
      )
    }

    if (
      minimatch(file, './src/styles/components/**/*.scss') ||
      minimatch(file, './src/styles/global/**/*.scss')
    ) {
      comments.push(
        'directory "Gaël: SCSS file should be co-located and imported within a component"'
      )
    }

    if (minimatch(file, './src/components/pages/Styleguide/**/*.jsx')) {
      comments.push(
        'directory "Gaël: this file should be migrated within storybook"'
      )
    }

    if (
      minimatch(file, './src/components/**/!(__specs__)/*.jsx') &&
      !minimatch(file, './src/components/pages/Styleguide/**/*.jsx')
    ) {
      comments.push(
        'directory "Gaël: this file should be migrated within the new directory structure"'
      )
    }

    if (minimatch(file, './src/components/hoc/**/!(__specs__)/*.js')) {
      comments.push('standard "Gaël: HOC should be replaced in favor of hooks"')
    }

    insertComments.forEach(useCase => {
      if (data.indexOf(useCase.match) >= 0) {
        comments.push(useCase.comment)
      }
    })

    if (comments.length > 0) {
      // console.log('---------------')
      // console.log(file)
      // console.log(comments)
      prependFile(
        file,
        `/*
${comments.map(text => comment(text)).join(`
`)}
*/

`
      )
    }
  })
})
