_minitel() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if (( COMP_CWORD == 1 )); then
        COMPREPLY=( $(compgen -W "key" -- "$cur") )
    elif [[ "${COMP_WORDS[1]}" == "key" ]] && (( COMP_CWORD == 2 )); then
        COMPREPLY=( $(compgen -W "start stop restart status test calibrate dump" -- "$cur") )
    fi
}
complete -F _minitel minitel
