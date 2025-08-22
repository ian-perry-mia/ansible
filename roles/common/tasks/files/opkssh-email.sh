#!/usr/bin/env bash

DENY_LIST="root admin email backup"

for deny_principal in $DENY_LIST; do
  if [ "$OPKSSH_PLUGIN_U" = "$deny_principal" ]; then
    echo "Access denied for principal: $OPKSSH_PLUGIN_U"
    exit 1
  fi
done

if [ "$OPKSSH_PLUGIN_U" = "$OPKSSH_PLUGIN_EMAIL"]; then
    echo "allow"
    exit 0
else
    echo "deny"
    exit 1
fi