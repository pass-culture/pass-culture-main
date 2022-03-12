---
to: <%= absPath %>/README.md
skip_if: <%= includeReadme === false %>
---
## <%= component_name %>

Vous pouvrez retrouver les example d'utilisations de [<%= component_name %> dans notre storybook](<%= storybookBaseUrl %>/?path=/story/<%= h.changeCase.lower(category) %>-<%= h.changeCase.lower(component_name) %>--c-1)

