# Completion script for the `pc` command
# To install this script:
# 1. Add the following line to your `~/.zshrc` file:
#    source /path/to/pc-completion.sh
#    (replace `/path/to/pc-completion.sh` with the actual path to your script)
# 2. Reload your `.zshrc` configuration with (or start a new terminal):
#    source ~/.zshrc
#

_pc_completions()
{
    local cur prev commands opts

    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # List of possible options
    opts="-h -e -b -f -t"
    
    # List of available commands
    commands="access-db-logs alembic bash diff-schema dump-db install install-hooks logs pgcli psql psql-file psql-test python rebuild-backend reset-all-db reset-db-no-docker reset-db-test-no-docker reset-all-storage restart-backend restart-api-no-docker restore-db restore-db-intact set-git-config setup-no-docker start-backend start-api-no-docker start-backoffice-no-docker start-pro symlink test-backend test-backoffice"

    # Completion for options
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    # Completion for commands
    if [[ ${prev} == "pc" ]] ; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi

    return 0
}
complete -F _pc_completions pc

