#!/bin/bash

cd "$(dirname "$0")" # Go to the script's directory
source lib/mo

INCLUDE() {
    cat "$MO_FUNCTION_ARGS"
}

TITLE=$2

cat << EOF | mo -u -s=$1 | tee $2.html
{{INCLUDE zonelet-post-template.mo}}
EOF