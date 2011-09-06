#!/bin/bash

ACTIVATION_KEY_NAME="activation_key_$RAND"
test "activation key create" activation_key create --name="$ACTIVATION_KEY_NAME" --description="key description" --environment="$TEST_ENV" --org="$TEST_ORG"
test "list activation keys by environment" activation_key list --environment="$TEST_ENV" --org="$TEST_ORG"
test "list activation keys by organization" activation_key list --environment="$TEST_ENV" --org="$TEST_ORG"
test "show activation key" activation_key info --org="$TEST_ORG" --name="$ACTIVATION_KEY_NAME"
test "delete activation key" activation_key delete --org="$TEST_ORG" --name="$ACTIVATION_KEY_NAME"
